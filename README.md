# What is this

This is a piece of software for tracking what applications you spend your time using, and how much you use them. This is
ideal for understanding the way that you spend time.

Each measurement of your computer usage saves a bit of information about the window that you had focused, it's title,
the window's classes. The number of keystrokes entered during or since the last measurement, the distance in pixels that
your mouse travels.

When you view the report that this software generates, each measurement is associated with a number of 'categories' or
`tags` which are viewed as intervals along the time during the day.

## Installation

timetracker currently only works on linux running XOrg. This software nevertheless requires additional permissions to
run. On most linux distributions, you will have to run this program under a user in the `input` group.

To add yourself to this group, run

```shell
sudo usermod -Ga input <your username> 
```

(To revert you can run `sudo gpasswd -d input <your username>`)

Once you have done this you may run `poetry run python -m timetracker` to start tracking your activity.

To generate a report, you may run `poetry run python -m timetracker.examplereport`, it is hosted at `127.0.0.1:8080` by
default.

### Report Configuration

Currently, while running `python -m timetracker.examplereport`, you may adjust your matchers and test them and save them
in the web interface.

Tags are split by commas, allowed matches are split into separate text boxes. Matches are case-insensitive.

#### Matcher types

**Simple Matchers**

These matchers are the most basic way to match a window. The first is the `name` matcher, which matches based on the
window title. Each name matcher may have multiple entries, only one of which needs to match the window title to be
considered a match.

The second is the class matcher, and that matches windows based on the presence of a class applied to the window. These
are often to specify the application that is running it for window management purposes, so it may be clearer than the
title in some cases.

**Logical Matchers**

Logical matchers combine the results from several of the other matchers types.

* *And Matcher* Must match all submatchers
* *Or Matcher* Must match at least one submatcher

