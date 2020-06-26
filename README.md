# doxy-next-gen

I'm a big fan of both [Doxygen](https://www.doxygen.nl/index.html) and 
[QDoc](https://doc.qt.io/qt-5/qdoc-index.html), but more recently, also 
[sphinx-doc](https://www.sphinx-doc.org/en/master/) and 
[Markdown](https://daringfireball.net/projects/markdown/).

I've also bumped in to various other interesting things over the years. E.g. 
the need to do requirements tagging and other metadata that would sit nice with
the Doxygen-style tags, as well as 
[Jinja2](https://jinja.palletsprojects.com/en/2.11.x/), which would be an 
awesome backend to Doxygen, instead of the fairly limited options given from 
the built in generators.

Being a fan of the various tooling built around clang and llvm, I started 
poking at this problem from this direction. Would it be possible to use clang, 
jinja2 and some hacked together Python code and actually implement a better 
documentation tool? Is _doxy-next-gen_ possible?

This repository represents my experiments in this direction. This is not 
production code. This is not a finished product. This is a collection of 
research experiments conducted ot find the various building blocks needed to 
build a next generation documentation tool.

# Goals

I meant to call this section requirements, but that is too strong a word. These
are some random goals I have:

* Somewhat compatible with Doxygen as well as QDoc sources.
* Capable of adding more metadata dynamically, i.e. define new tags in some 
  sort of configuration and then extract them in a backend.
* Modern markup support, e.g. Markdown.
* Flexible output generators (backends) based on a model and Jinja2 template.
* Possibility to do rules checking on the model, including custom tags. E.g. 
  ensure all classes has a _maintainer_ tag declared or similar.
* Not bound to any particular language...
* ...but basing the initial model around clang and C++

The last two goals are fun. What I'm trying to say is, don't paint yourself 
into a corner, but also, don't solve all the problems at once.

# References

These are some interesting links I've picked up along the way:

* https://eli.thegreenplace.net/2011/07/03/parsing-c-in-python-with-clang
* https://www.mobibrw.com/2019/16782
* https://stackoverflow.com/questions/40292703/how-can-i-retrieve-fully-qualified-function-names-with-libclang
* http://llvm.org/devmtg/2012-11/Gribenko_CommentParsing.pdf - exactly this

# Experiments

The current experiments, described in `parser.py` try to accomplish the 
following:

* Locate and extract comment blocks.
* 

# Usage

## Installing it

This is a python project intended to be run using python3 and a venv. The 
recommended way to go about this is something like this:

```
python3 -m venv .
. bin/activate
pip install -r requirements.txt
```

## Running it

I'm using debian and have installed the `libclang-10-dev` package from which 
I'd like the `clang` python package to pick up the `libclang.so` file. To make 
this happen, I have to specify an appropriate `LD_LIBRARY_PATH`, in my case 
something like this:

```
LD_LIBRARY_PATH=/usr/lib/llvm-10/lib/ python3 parser.py example.cpp
```

This will run the various parts I've built on the provided `example.cpp` file.

# Licensing

Doxy-next-gen is a development tool, and is made available under GPLv3.

> doxy-next-gen - a documentation extractor and generator
> Copyright (C) 2020 Johan Thelin
>
> This program is free software: you can redistribute it and/or modify
> it under the terms of the GNU General Public License as published by
> the Free Software Foundation, either version 3 of the License, or
> (at your option) any later version.
>
> This program is distributed in the hope that it will be useful,
> but WITHOUT ANY WARRANTY; without even the implied warranty of
> MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
> GNU General Public License for more details.
>
> You should have received a copy of the GNU General Public License
> along with this program.  If not, see <https://www.gnu.org/licenses/>.

Document generation templates, as well as configurations defining tags are not considered derived work and may thus be developed and distributed without adhering to GPLv3. 

It is, however, encouraged to distribute such work under an open source license, be it permissive or strong. Sharing is caring.
