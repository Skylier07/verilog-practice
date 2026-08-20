Behavior:
```
reset
  ↓
q = 0

load
  ↓
q = parallel_in

enable
  ↓
shift q right by one
serial_in enters the MSB

otherwise
  ↓
q stays unchanged
```


Priority:
```
reset > load > enable > hold
```