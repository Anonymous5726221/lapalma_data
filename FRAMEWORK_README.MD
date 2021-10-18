# Basic framework for Dash incorporating Bootstrap
this is a very basic framework to make the code easier to use and read.

The software is divided into different parts:
- Components;
- ViewModules;
- Callbacks;
- Data.

## Components
In the `components` folder every python file contains its own `component`.
A component is an object that makes use of the following packages `dash-html`, `dash-dcc` or `dash-bootstrap`.

## ViewModules
The `viewmodules` folder consists of python files that make up the html structure for a `view`.
As of right now, every .py file is its own page or view.

Each view as of now needs to be added to `pagecallbacks.py` and if the page itself doesn't exist it has to be added to `sidebar.py`.

The `view` is automatically added to the base layout of the DashApp.

## Callbacks
In the `callbacks` folder every callback has its own seperate .py file.

## Data
The database

---
# Getting started
## 1. adding a new view
Simply add a new python file in the `viewModules` folder and build the html structure with `dash-html`.

Add the variable to `__init__.py`:
`from .[pythonname] import [variable name]`

Go to `callbackModules/pagecallbacks.py` and add a new condition to `render_page_content`.

The view is now callable.

## 2. Adding a plot
A plot is part of `dcc`, `dcc.Graph` needs to be added to the html structure of the `view`, don't forget to give the graph an `id` so it's callable.

Create a new `callback` .py in `callbackModules`, link to the database and create a figure. Link the output to the `id` of the graph in the newly created `view`.

Now whenever the `view` is loaded the figure will also be displayed.
