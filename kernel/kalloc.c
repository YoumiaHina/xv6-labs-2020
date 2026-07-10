// Physical memory allocator, for user processes,
// kernel stacks, page-table pages,
// and pipe buffers. Allocates whole 4096-byte pages.

#include "types.h"
#include "param.h"
#include "memlayout.h"
#include "spinlock.h"
#include "riscv.h"
#include "defs.h"

void freerange(void *pa_start, void *pa_end);

extern char end[]; // first address after kernel.
                   // defined by kernel.ld.

struct run {
  struct run *next;
};

struct {
  struct spinlock lock;
  struct run *freelist;
} kmem[NCPU];

void
kinit()
{
  for(int i = 0; i < NCPU; i++)
    initlock(&kmem[i].lock, "kmem");
  freerange(end, (void*)PHYSTOP);
}

void
freerange(void *pa_start, void *pa_end)
{
  char *p;
  p = (char*)PGROUNDUP((uint64)pa_start);
  for(; p + PGSIZE <= (char*)pa_end; p += PGSIZE)
    kfree(p);
}

// Free the page of physical memory pointed at by v,
// which normally should have been returned by a
// call to kalloc().  (The exception is when
// initializing the allocator; see kinit above.)
void
kfree(void *pa)
{
  struct run *r;
  int id;

  if(((uint64)pa % PGSIZE) != 0 || (char*)pa < end || (uint64)pa >= PHYSTOP)
    panic("kfree");

  // Fill with junk to catch dangling refs.
  memset(pa, 1, PGSIZE);

  r = (struct run*)pa;

  // A process can migrate only while interrupts are enabled.  Keep the CPU
  // number stable until the page is linked into that CPU's free list.
  push_off();
  id = cpuid();
  acquire(&kmem[id].lock);
  r->next = kmem[id].freelist;
  kmem[id].freelist = r;
  release(&kmem[id].lock);
  pop_off();
}

// Allocate one 4096-byte page of physical memory.
// Returns a pointer that the kernel can use.
// Returns 0 if the memory cannot be allocated.
void *
kalloc(void)
{
  struct run *r;
  int id;

  push_off();
  id = cpuid();

  acquire(&kmem[id].lock);
  r = kmem[id].freelist;
  if(r)
    kmem[id].freelist = r->next;
  release(&kmem[id].lock);

  // Most allocations are satisfied locally.  If this CPU runs dry, take
  // roughly half of another CPU's pages so the relatively expensive steal
  // is amortized over many subsequent allocations.
  if(r == 0){
    for(int donor = 1; donor < NCPU && r == 0; donor++){
      int other = (id + donor) % NCPU;
      struct run *batch, *last, *local;
      int n = 0;

      acquire(&kmem[other].lock);
      for(struct run *p = kmem[other].freelist; p; p = p->next)
        n++;

      if(n != 0){
        int take = (n + 1) / 2;
        batch = kmem[other].freelist;
        last = batch;
        for(int i = 1; i < take; i++)
          last = last->next;
        kmem[other].freelist = last->next;
        last->next = 0;
      } else {
        batch = 0;
        last = 0;
      }
      release(&kmem[other].lock);

      if(batch){
        r = batch;
        local = batch->next;
        r->next = 0;
        if(local){
          acquire(&kmem[id].lock);
          last->next = kmem[id].freelist;
          kmem[id].freelist = local;
          release(&kmem[id].lock);
        }
      }
    }
  }

  pop_off();

  if(r)
    memset((char*)r, 5, PGSIZE); // fill with junk
  return (void*)r;
}
