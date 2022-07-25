# Recipes Calculator-LP
This is a generic recipe calculator for Factorio, Satisfactory, and other automation game alike, using the scipy linear programmng optimization library.\
The is **ONLY** a calculator, which does not contain any in-game information (thus generic). If you want to use it you should provide the data of the game and wrap it with your own class.

## Data Representation & Intialization
RecipeMatrix, the core class, is a wrapper for a 2d-numpy-array. It provides some features useful for later calculations.\
The class need basically four things, recipe matrix & a list of raw resources for intialization, and target output & priorities for calling the Solve method.
### matrix
You should put the recipes of the game in the form of a recipe graph, with row representing item and column representing recipe. Here's a small part of the oil production pipeline from Factorio,\
\
Ley say we have 5 items: `heavy oil`, `light oil`, `petroleum-gas`, `water`, `oil`, with the following recipes:\
        `40 heavy oil + 30 water = 30 light oil`\
        `30 light oil + 30 water = 20 petroleum-gas`\
        `100 crude oil = 30 heavy oil + 30 light + 40 petroleum-gas`\
        `100 crude oil + 50 water = 10 heavy oil + 45 light oil + 55 petroleum-gas`\

That gives us the matrix: \
`[[-40, 0, 30, 10],`\
`[30, -30, 30, 45],`\
`[0, 20, 40, 55],`\
`[-30, -30, 0, -50],`\
`[0, 0, -100, -10 ],]`\
(A Graph!)
By doing this we can ignore the recipe and item names, only focus on the structure of the items. Of course you want to build a functional calculator
