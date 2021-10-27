The current chart api is untenable and unexpandable.

It is impossible to add new types of charts in, it is impossible to add much flexibility, and in general, it's hastily
put together.

Does this mean we should just go to making this a matplotlib adapter? That'd probably be fine tbh.

Anyway, it needs to be able to:

* abstract into a number of different types of charts
  * Bar
  * Pie
  * Line
* It must be able to group categories together
  * Categories should probably only show up on the most specific one.
  * Nested grouping would allow further improvement :)
  * Honestly this will probably also need some hooks in the filter stuff, 
    or at least another layer on top
    
    Hard to say.
  * 
