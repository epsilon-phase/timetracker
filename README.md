# What is this

This is a piece of software for tracking what applications you spend your time using, and how much you use them. This is
ideal for understanding the way that you spend time.

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

Currently there is no easy way to customize the way that the windows are classified, the first way is to directly
edit `timetracker/examplereport.py`. The second way is to 