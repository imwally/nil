Title: Implementing a Stack That Supports Nested Transactions
Date: 2018-07-06T16:15:00-0400
Category: meta


[Kyle](https://kyleisom.net/) mentioned that in one of his recent
technical interviews he was asked to implement a
[stack](https://en.wikipedia.org/wiki/Stack_(abstract_data_type)) that
supports nested transactions. Since I've been trying to brush up on my
data structures and algorithms skills and prepare myself for such
interviews I thought this would be a fun exercise to tackle. Fortunately
I went on vacation shortly after he mentioned this so I had some time to
think about it. Not sure how well I would fare in an interview
environment but I suppose that's for a different post.

Not So Basic Operations
-----------------------

Of course this data structure should support the basic stack operations
of `Push()`, `Pop()` and even `Peek()`, an operation that returns the
next value that would be popped without actually popping it off the
stack. Implementing these operations are relatively straight forward.
The interesting part however is when you start thinking about handling
nested transactions. What happens if you begin a new transaction, push a
few values on the stack but decide to rollback? One option would be to
track these values in a temporary location and only apply them to the
stack once a commit or rollback takes place. But how do you actually
*handle* these temporary values?

The Structure
-------------

I decided to use [Go](https://golang.org/) to write this implementation
so all methods will be written on the `txstack.Stack` type.

Here's what the struct looks like:

```
type Stack struct {
	Storage    [][]int
	InTx       bool
	Pointer    int
	TxCommitted int
}
```

The most interesting field in this struct is the `Storage` slice. More
precisely, it's a slice of slices of type `int`. This is where the
so-called *magic* happens. The other three fields will become apparent
after I describe the nested transaction functionality.

Transactions and Nesting
------------------------

Transactions occur after a `Begin()` call. This is when the `InTx` field
is set to `true`. Basic operations can still take place before a
transaction begins but all operations afterwards are in a temporary
state. What this means is that the operations won't be applied to the
stack until a `Commit()` takes place, or, if a `Rollback()` happens, all
operations after the `Begin()` will be discarded. A transaction ends
when either a rollback takes place or when the number of commits match
the number of begins.

That last sentence could use a bit of unpacking. Essentially what it
means is that when a `Begin()` takes place both the `Pointer` and
`Committed` fields are incremented. The pointer keeps track of the
current transaction state (operations are done on the storage at index
`Pointer`) and when a `Commit()` takes place the `Committed` int is
decremented. When this field reaches 0 all nested commits have taken
place so all temporary stacks can be flushed and the latest stack gets
copied into `Storage` at index 0.

Example:

```
s := txstack.New()
s.Push(3)
s.Push(2)
s.Push(1)
```

State:

```
+ - +
| 1 |
+ - +
| 2 |
+ - +
| 3 |
+ - +
```

No transactions have taken place. That is the stack as it stands.

```
s.Begin()
s.Pop()
```

Temporary State:

```
+ - +
| 2 |
+ - +
| 3 |
+ - +
```

A new transaction has begun creating a temporary state of the stack.

```
s.Rollback()
```

State:

```
+ - +
| 1 |
+ - +
| 2 |
+ - +
| 3 |
+ - +
```

The stack looks the same before the `Begin()` took place because of the
call to `Rollback()`. If a call to `Commit()` happened instead then
obviously the temporary state would have become the permanent state.

Handling State
--------------

Each time a new transaction begins a new temporary stack is created.
This is where the `Storage` and `Pointer` fields comes in. A new slice
is created, the contents of the previous slice are copied into it and
the pointer is incremented. Now, all methods are done on the stack that
the pointer points to.

Given the same example from above the internal state of the data
structure would look like the following:

```
s := txstack.New()
s.Push(3)
s.Push(2)
s.Push(1)
```

Internal State:

```
Stack {
	Storage: [[3,2,1]],
	InTx: false,
	Pointer: 0,
	Committed: 0,
}
```

```
s.Begin()
s.Pop()
```

Internal State:

```
Stack {
	Storage: [[3,2,1],[3,2]],
	InTx: true,
	Pointer: 1,
	Committed: 1,
}
```

```
s.Rollback()
```

Internal State:

```
Stack {
	Storage: [[3,2,1]],
	InTx: false,
	Pointer: 0,
	Committed: 0,
}
```

If `Commit()` was called instead of `Rollback()` then the `Committed`
field would be set to 0. When this happens the last slice gets copied
into index 0 and the other slices are removed.

Putting the whole `txstack` package together:

```
package txstack

type Stack struct {
	Storage     [][]int
	InTx        bool
	Pointer     int
	TxCommitted int
}

// flushTxStacks will flush all temp storage stacks while only
// retaining the stack at storage location p by copying it into
// storage location 0.
func (s *Stack) flushTxStacks(p int) {
	keepStack := s.Storage[p]

	storage := make([][]int, 1)
	for _, val := range keepStack {
		storage[0] = append(storage[0], val)
	}
	s.Storage = storage
}

func (s *Stack) inTx() bool {
	return s.InTx
}

func (s *Stack) Empty() bool {
	p := s.Pointer
	if len(s.Storage[p]) != 0 {
		return false
	}

	return true
}

func (s *Stack) Size() int {
	p := s.Pointer
	return len(s.Storage[p])
}

func (s *Stack) Push(val int) {
	p := s.Pointer
	s.Storage[p] = append(s.Storage[p], val)
}

func (s *Stack) Pop() int {
	p := s.Pointer
	val := s.Storage[p][s.Size()-1]
	s.Storage[p] = s.Storage[p][:s.Size()-1]

	return val
}

func (s *Stack) Peek() int {
	p := s.Pointer
	return s.Storage[p][s.Size()-1]
}

// Begin creates a new transaction by making a new temporary slice and
// copying the last storage into it. Only when a full commit or
// rollback takes place will the temporary stacks be flushed.
func (s *Stack) Begin() {
	s.InTx = true
	newStack := make([]int, s.Size())

	p := s.Pointer
	copy(newStack, s.Storage[p])

	s.Storage = append(s.Storage, newStack)

	s.Pointer++
	s.TxCommitted++
}

// Commit decrements the internal TxCommitted counter and when a full
// commit takes place (when the counter reaches 0) it flushes all
// stacks while only retaining the latest.
func (s *Stack) Commit() {
	s.TxCommitted--
	if s.TxCommitted == 0 {
		s.flushTxStacks(s.Pointer)
		s.Pointer = 0
	}
}

func (s *Stack) Rollback() {
	s.flushTxStacks(0)
	s.Pointer = 0
	s.TxCommitted = 0
	s.InTx = false
}

func New() Stack {
	storage := make([][]int, 1)
	return Stack{
		Storage:     storage,
		InTx:        false,
		Pointer:     0,
		TxCommitted: 0,
	}
}
```

It could certainly use some more work like implementing error handling
and watching for underflows and overflows but it works and I'm pretty
happy with the outcome. Interestingly there isn't much on the web about
writing a stack like this. Actually, I couldn't find anything but
information about SQL transactions. This made it even more satisfying
when all the tests passed.
