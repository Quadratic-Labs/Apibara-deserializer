# Apibara Deserializer

<details open ="open">
<summary>Table of Contents</summary>

- [About](#about)
- [Install](#install)

</details>

# About
>Converts Starknet event data from bytes to Python data types

Our [Moloch on Starknet indexer](https://github.com/Quadratic-Labs/Moloch-on-Starknet-indexer) is based on [Apibara python indexer Template](https://github.com/apibara/python-indexer-template), which enables to quickly start indexing smart contracts events with [Apibara](https://github.com/apibara/apibara).

As our indexer handles a dozen of events which are sent by apibara as bytes, we developed a generic function to convert them to Python data types in order to facilitate the update of the mongoDB database. 

# Install

```bash
git clone https://github.com/Quadratic-Labs/Apibara-deserializer.git
cd Apibara-deserializer
pip install .
```
