# Introduction
This is an open-source version of the Graph Builder provided in
JMP. Though JMP is developed by SAS and has a large number of
statistical test and model building interfaces, its most used feature in
industry is plotting and the Graph Builder is particularly good for data
exploration.

Plotly already has Chart Studio which is highly analogous in
functionality to Graph Builder, which also extends to be able to do
data transforms in the UI and so is like a subset of JMP.

# Planned Features
Copied:
- Different plot types supported (line, scatter, bar)
- Multiple x- and y-axes (shared) as subplots 
- Composite axes for categorical variables (multicategory axes)
- Moving average or smoothing fits for legend groups
- Data type inference
- Easy conversion between column data that happens automatically (is inferred)
  in plotting. For example, if color by a continuous variable is desired, that
  can either be a gradient, or it can be discretized by the quantiles, say 5
  quantiles of [0,20%), [20%,40%), [40%,60%), [60%,80%), [80%,100%). If size by a
  categorical data is desired, then each category can be assigned a size by
  making a linear space in a pixel range of the scale (what is commonly called
  factorization). 
- Dynamic filter creation, filter ranges for continuous variables and sets for discrete variables.

Additional:
- Easy column aliasing for data sets with long/ununintuitive column names.
- Easy conversion between column data types for the data table (similar to aliasing) 
- Easy column concatenation for string columns to make new legending labels 
- Easy selection of items to be displayed in hover text
- Caching of user settings for filters (not yet implemented, see https://community.plotly.com/t/save-the-app-state-feature-request/5509)

# Program Notes

The dash framework abstracts many problems away making the building of
this app almost like an enumeration of the inputs and outputs. There
are condition dependent routines on the inputs, e.g., plotting routine
depends on plot type selected. However this is mostly articulating
what is the desired output for a given set of inputs, since even the
lower-level `plotly.graph_objects` module is like the matplotlib API.

The biggest difficulties are in making the program readable and
efficient.  Readibility is in reducing repetition of instructions,
efficiency is in writing instructions which are both theoretically
efficient in time and space complexity and consider how the interpreter
will compile it/hardware will run it, in particular, automatic
vectorization.

## Dynamically Created Elements

Local filters are an example of a dynamically created element since it
isn't known how many local filters a user will want. A work-around is
to define a large number of invisible local filters, say 5, and to then
update their state to visible when the user adds local filters. In fact
this visibility updating for static elements is used in some parts of
the program. However generally applications should change the input
form depending on the current user input, which requires web elements
(HTML or dash core components) to be dynamically created and dynamically
assigned to callback routines. This feature was implemented in Dash
1.11.0 under the title "pattern matching callbacks" and is explained
well in the documentation. 

## HTML and CSS

Like JMP, this is designed only for desktop use, so it is expected a
greater than 1000 pixel width display is used and there is no screen
size adaptation.

Dash default core component styling is used.

## Program Efficiency and Caching

It is assumed that Dash's scalable design, both through its use of
React.js for single page application and asynchronous communications on
client side and its stateless WSGI server side, makes this application
efficient for use cases of interest, at least until all planned features
have been developed. It is possible to use, e.g., a SQL connection
to update a database so callbacks can effectively pass data between
each other server-side. There exist other means of accomplishing this
server-side, such as per user session caches.

Memory overuse and slow process time are more likely come from
inefficient routines which containerize the data being input to the
plotting API, and the plotting API itself. For example, for marker plots
several times speedup is achieved with go.Scattergl over go.Scatter.

# Mathematics Notes

## Curve Fitting

Polynomial fits only require solving the problem Ax = b for the
coefficients, but is subject to polynomial wiggle and is unsuitable for
large number of data points with high noise, the most common scenario
in statistics applications of the industry. There are python bindings
to fortran libraries for fitting splines in the scipy package which may
be used. Splines are matching third derivatives in an interpolation,
and fit all data points, therefore also being unsuitable. Often what
people call splines are actually smoothers, which don't interpolate (fit
exactly) all the points. This ambiguity might arise because sometimes
splines are used with a post-process smoothing parameter. The smoother
given here is the Whittaker-Ellis smoother. Similar trend lines to
smoothers can be obtained by moving averages. Both smoothing and moving
averages are implemented.
