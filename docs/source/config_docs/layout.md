# Layouts

Layout algorithms are used to define the token placements. The algorithms try to achieve minimal page usage, and most of them try to maximize contiguous token placement. The algorithms are defined in the root of the configuration file under the keys specified below.

## Layout Algorithm Selection
The `layout` key in the configuration file defines the layout algorithm to use. The following options are available:
- `rectpack_best`: A default combination of rectpack algorithms that produces the best results. (Default)
- `rectpack`: Any of the rectpack algorithms. See below.
- `greedy`: A greedy algorithm that places tokens in the order they are defined in the configuration file.
- `all`: Best result from applying all available layout algorithms.

## Rectpack Algorithms
The `rectpack` python library provides many layout algorithms (and combinations thereof). 
For each key below, the value can be a list of possible values instead. For every cross-product of the values, a layout is generated. The final algorithm is to produce the best result from all generated layouts.
These are deterimined with the following keys:
- `bin_algo`: The bin packing sub-algorithm to use. Options are: `BNF`, `BFF`, `BBF` and `Global`. (Default:`BNF`)
- `sort_algo`: The sorting algorithm to use. Options are: `AREA`,`PERI`,`DIFF`,`SSIDE`,`LSIDE`,`RATIO`, and `NONE`. (Default:`AREA`)
- `pack_algo`: The packing algorithm to use. Options are: 
 - ```
    GuillotineBssfSas, GuillotineBssfLas, 
    GuillotineBssfSlas, GuillotineBssfLlas, GuillotineBssfMaxas, 
    GuillotineBssfMinas, GuillotineBlsfSas, GuillotineBlsfLas, 
    GuillotineBlsfSlas, GuillotineBlsfLlas, GuillotineBlsfMaxas, 
    GuillotineBlsfMinas, GuillotineBafSas, GuillotineBafLas, 
    GuillotineBafSlas, GuillotineBafLlas, GuillotineBafMaxas, 
    GuillotineBafMinas,

    MaxRectsBl, MaxRectsBssf, MaxRectsBaf, MaxRectsBlsf

    SkylineMwf, SkylineMwfl, SkylineBl, 
    SkylineBlWm, SkylineMwfWm, SkylineMwflWm
    ```
    (Default:`GuillotineBssfSas`)

#### Generated Configurations
If the `layout` is `rectpack`, the layout algorithms are generated as described above (cross-product of the values).
If the `layout` is `rectpack_best`, the following configuration combinations are used:
- `bin_algo`: Default (`BNF`)
- `pack_algo`: `"GuillotineBssfSas", "MaxRectsBssf", "SkylineMwf"`
- `sort_algo`: `"AREA"`
- `rotation`: `true` (if not already set)


