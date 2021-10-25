* [ ] Make the database connection instanceable
* [ ] Write tests for various things
    * [ ] The Matching infrastructure
    * [ ] Chart thing, maybe?
        * [ ] Color Chooser should at least be doable
* [ ] Write documentation
    * [ ] Python docstrings
    * [ ] Configuration guide
    * [ ] Chart customization
* [ ] Write new things
    * [ ] Improve chart API with higher level abstractions

      Bit fiddly for a graphics program huh?
        * [ ] Improve generated svg
            * [x] Generate sensible class names for blocks to permit scripting and shit
            * [ ] Add customization to the chart API
                * [ ] Colors
                * [ ] Shapes
                    * [ ] Circle, radius of each circle on the timeline shows how long it was for.
                    * [ ] Squares, same as above
            * [ ] Make it interactive
                * [ ] User configurable tagging and such, saved somewhere local for convenience later.
                * [ ] Use websockets to stream updates in a more efficient and pleasing fashion
                    * Maybe worth using D3 or something.
    * [ ] Better color choosers
        * [ ] Dependent tags

          Should be detectable. Layout will be challenging, but it will be an improvement I think — Trace
        * [ ] "smart" color choosers. Write some weird heuristic designed to match specific inputs and outputs with no
          care given to the rest.
    * [ ] Mouse Activity intensity

      This seems like it might actually be really hard to make given a static polling frequency.
      Given the switch to libinput, this enables, potentially, *much* more accurate tracking. 
        * [x] Keyboard activity detection

          Is this possible to do without hooking into something horrible and low level?
        
    * [ ] Do it for other platforms. Windows and mac osx should be doable, wayland... maybe not?
      
      At least, it'll be more complicated to do for wayland due to the fact it isn't part of the protocol.
      * [ ] Mac osx
      * [ ] Windows
    * [ ] Add color customization
    * [ ] Permit having the chart data in a specific order
    * [ ] include option to show all the data series, even if they are empty.
      
      This will require additional communication from the chart class to the chartpart class. This may be
      better served by refactoring to make the overall design more... expansible
    * [ ] Add alternative views other than the rectangle chart
      * [ ] Pie chart
      * [ ] Bar chart per hour, showing all tasks