# Recipes Calculator-LP
This is a generic recipe calculator for Factorio, Satisfactory, and other automation game alike, using the scipy linear programmng optimization library.\
The is **ONLY** a calculator, which does not contain any in-game information (thus generic). If you want to use it you should provide the data of the game and wrap it with your own class.

## Data Representation & Intialization
RecipeMatrix, the core class, is a wrapper for a 2d-numpy-array. It provides some features useful for later calculations.\
The class need basically four things, recipe matrix & a list of raw resources for intialization, and target output & priorities for calling the Solve method.
