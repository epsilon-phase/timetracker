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
            * [ ] Use group transforms to avoid needing to put x attributes on rectangles
            * [ ] Generate sensible class names for blocks to permit 
    * [ ] Better color choosers
        * [ ] Dependent tags

          Should be detectable. Layout will be challenging, but it will be an improvement I think — Trace
        * [ ] "smart" color choosers. Write some weird heuristic designed to match specific inputs and outputs with no
          care given to the rest.
    * [ ] Mouse Activity intensity

      This seems like it might actually be really hard to make given a static polling frequency.
        * [ ] Keyboard activity detection

          Is this possible to do without hooking into something horrible and low level?