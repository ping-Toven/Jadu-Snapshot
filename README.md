# Jadu-Snapshot

These files can be used in a few ways to take snapshots of existing Jadu NFT collections on Ethereum.

- HoverboardSnapshot.py & Jetpack Snapshot.py use the Pandas module to store data and export CSV files of the snapshot when the script is run
- SQL Snapshot.py uses the sqlite3 module to snapshot either of the collections based on command line input and updates an existing db file ( hb_snapshot.db & jp_snapshot.db ) as needed.
- snapshot_db.py is the helper class that handles executing SQL queries and contains the update as necessary logic. Will be expanded to use the data for interesting queries.
