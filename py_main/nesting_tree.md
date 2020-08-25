# Overview of nesting_tree.py:
The class uses the following naming convention when combining nesting trees:
*Attributes*
  - *self.attr:* For *attr* in {inp,out,int,fg,wT,map_all} self.attr indicates the union of sets from all nesting trees. 
    * *inp:* Inputs in aggregate sector,
    * *out:* outputs in aggregate sector,
    * *int:* intermediate goods in aggegregate sector,
    * *fg:* Union of inp and out (final goods)
    * *wT:* Union of int and inp (prices with taxes are defined over this)
    * *map_all:* mappings from knots-to-branches in aggregate sector (union of maps for each tree).
  - *Hep*
