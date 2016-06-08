# unidw
Early work on a Unicon data warehouse to take exported time tracking data and put it into a star schema for 
more extensive reporting and analysis than can be done in the time tracking system today and more easily
than in spreadsheets.

The intent was one or more star schemas that support a variety of roll-up reporting capabilities as well as ad hoc reporting.  So far, the single star consists of a fact table of timecard entries.  Rows in the fact table reference person (employee), time, and task dimensions.  

The target environment for this is AWS Redshift, but at this point, there is nothing Redshift specific, no indexing or analysis of access patters has been done.

**Note:** This is quite possibly all junk and fit to be tossed.

Generally, here is what is contained:

1. SQL Power Architect model
2. DDL for the star schema tables (Gen'ed by Power Arch)
3. Python Scripts to populate the dimension tables from flat-file exports from Replicon
4. Start on a python script to populate the fact table - probably no value
