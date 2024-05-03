python ./main ..\images\test1-number\ ..\fonts\test1-number

To run this program, please install these requirements:

### Potrace

unzip the package in `/potrace/installer`, and copy the executable file into `/potrace/bin`.

### FontForge

I really recommand using this program under Linux enviroment. It is inconvinient to use fontforge as a python extention under Windows. 

#### FontForge as a python extension

If you have configured fontforge with the --enable-pyextension argument, then when fontforge installs itself it will also set itself up as something that can be used inside of python (up until now we have been talking about using python inside of fontforge).

```shell
$ ./configure --enable-pyextension
$ make
$ sudo make install
```

once you do that you can invoke all of the above fontforge commands from inside of python by saying:

```python
>>> import fontforge
```