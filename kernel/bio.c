// Buffer cache.
//
// The buffer cache is a linked list of buf structures holding
// cached copies of disk block contents.  Caching disk blocks
// in memory reduces the number of disk reads and also provides
// a synchronization point for disk blocks used by multiple processes.
//
// Interface:
// * To get a buffer for a particular disk block, call bread.
// * After changing buffer data, call bwrite to write it to disk.
// * When done with the buffer, call brelse.
// * Do not use the buffer after calling brelse.
// * Only one process at a time can use a buffer,
//     so do not keep them longer than necessary.


#include "types.h"
#include "param.h"
#include "spinlock.h"
#include "sleeplock.h"
#include "riscv.h"
#include "defs.h"
#include "fs.h"
#include "buf.h"

#define NBUCKET 13

struct bucket {
  struct spinlock lock;
  struct buf head;
};

struct {
  // Cache hits need only one bucket lock.  Misses use evict_lock to make
  // lookup plus replacement atomic, preserving one cached copy per block.
  struct spinlock evict_lock;
  struct bucket bucket[NBUCKET];
  struct buf buf[NBUF];
} bcache;

static uint
bhash(uint blockno)
{
  return blockno % NBUCKET;
}

// The caller holds bucket[h].lock.
static void
binsert(uint h, struct buf *b)
{
  struct buf *head = &bcache.bucket[h].head;
  b->next = head->next;
  b->prev = head;
  head->next->prev = b;
  head->next = b;
}

// The caller holds the lock for the bucket containing b.
static void
bremove(struct buf *b)
{
  b->next->prev = b->prev;
  b->prev->next = b->next;
}

void
binit(void)
{
  struct buf *b;

  initlock(&bcache.evict_lock, "bcache.evict");
  for(int i = 0; i < NBUCKET; i++){
    initlock(&bcache.bucket[i].lock, "bcache.bucket");
    bcache.bucket[i].head.prev = &bcache.bucket[i].head;
    bcache.bucket[i].head.next = &bcache.bucket[i].head;
  }

  for(b = bcache.buf; b < bcache.buf + NBUF; b++){
    // Give unused buffers impossible device identities, and spread them
    // across buckets so the initial cache structure is balanced.
    b->dev = (uint)-1;
    b->blockno = b - bcache.buf;
    b->valid = 0;
    b->refcnt = 0;
    b->lastuse = 0;
    initsleeplock(&b->lock, "buffer");
    binsert(bhash(b->blockno), b);
  }
}

// Look through buffer cache for block on device dev.
// If not found, allocate a buffer.
// In either case, return locked buffer.
static struct buf*
bget(uint dev, uint blockno)
{
  struct buf *b, *victim;
  uint h = bhash(blockno);
  uint oldh, oldest;

  // The common case touches only the requested block's bucket.
  acquire(&bcache.bucket[h].lock);
  for(b = bcache.bucket[h].head.next;
      b != &bcache.bucket[h].head; b = b->next){
    if(b->dev == dev && b->blockno == blockno){
      b->refcnt++;
      release(&bcache.bucket[h].lock);
      acquiresleep(&b->lock);
      return b;
    }
  }
  release(&bcache.bucket[h].lock);

  // Serialize misses.  Recheck after acquiring the eviction lock because
  // another CPU may have installed this block while we were waiting.
  acquire(&bcache.evict_lock);
  acquire(&bcache.bucket[h].lock);
  for(b = bcache.bucket[h].head.next;
      b != &bcache.bucket[h].head; b = b->next){
    if(b->dev == dev && b->blockno == blockno){
      b->refcnt++;
      release(&bcache.bucket[h].lock);
      release(&bcache.evict_lock);
      acquiresleep(&b->lock);
      return b;
    }
  }
  release(&bcache.bucket[h].lock);

retry:
  // Find the least-recently-used unreferenced buffer.  We inspect one
  // bucket at a time; a candidate is validated again before replacement.
  victim = 0;
  oldh = 0;
  oldest = 0;
  for(uint i = 0; i < NBUCKET; i++){
    acquire(&bcache.bucket[i].lock);
    for(b = bcache.bucket[i].head.next;
        b != &bcache.bucket[i].head; b = b->next){
      if(b->refcnt == 0 && (victim == 0 || b->lastuse < oldest)){
        victim = b;
        oldh = i;
        oldest = b->lastuse;
      }
    }
    release(&bcache.bucket[i].lock);
  }

  if(victim == 0){
    release(&bcache.evict_lock);
    panic("bget: no buffers");
  }

  acquire(&bcache.bucket[oldh].lock);
  if(victim->refcnt != 0 || bhash(victim->blockno) != oldh ||
     victim->lastuse != oldest){
    release(&bcache.bucket[oldh].lock);
    goto retry;
  }

  // Reserve the victim before changing its identity.  If it moves between
  // buckets, no other path can deadlock with these two locks: ordinary hits
  // hold one bucket and other evictions are serialized by evict_lock.
  victim->refcnt = 1;
  if(oldh != h){
    bremove(victim);
    acquire(&bcache.bucket[h].lock);
    victim->dev = dev;
    victim->blockno = blockno;
    victim->valid = 0;
    binsert(h, victim);
    release(&bcache.bucket[h].lock);
  } else {
    victim->dev = dev;
    victim->blockno = blockno;
    victim->valid = 0;
  }
  release(&bcache.bucket[oldh].lock);
  release(&bcache.evict_lock);

  acquiresleep(&victim->lock);
  return victim;
}

// Return a locked buf with the contents of the indicated block.
struct buf*
bread(uint dev, uint blockno)
{
  struct buf *b;

  b = bget(dev, blockno);
  if(!b->valid) {
    virtio_disk_rw(b, 0);
    b->valid = 1;
  }
  return b;
}

// Write b's contents to disk.  Must be locked.
void
bwrite(struct buf *b)
{
  if(!holdingsleep(&b->lock))
    panic("bwrite");
  virtio_disk_rw(b, 1);
}

// Release a locked buffer.
// Record its release time for later LRU eviction.
void
brelse(struct buf *b)
{
  uint h;

  if(!holdingsleep(&b->lock))
    panic("brelse");

  releasesleep(&b->lock);

  h = bhash(b->blockno);
  acquire(&bcache.bucket[h].lock);
  b->refcnt--;
  if(b->refcnt == 0)
    b->lastuse = ticks;
  release(&bcache.bucket[h].lock);
}

void
bpin(struct buf *b) {
  uint h = bhash(b->blockno);
  acquire(&bcache.bucket[h].lock);
  b->refcnt++;
  release(&bcache.bucket[h].lock);
}

void
bunpin(struct buf *b) {
  uint h = bhash(b->blockno);
  acquire(&bcache.bucket[h].lock);
  b->refcnt--;
  if(b->refcnt == 0)
    b->lastuse = ticks;
  release(&bcache.bucket[h].lock);
}
