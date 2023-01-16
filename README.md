# Apibara Deserializer

<details open ="open">
<summary>Table of Contents</summary>

- [About](#about)
- [Story](#story)
- [Install](#install)

</details>

# About
Convert Starknet event data from bytes to Python data types


# Story
Our Apibara indexer handles a dozen of events which are sent by apibara as bytes, we needed to convert them to Python data types to be able to understand what's in there and update the database accordingly so we wrote a generic function that handles all the events we had and we decided to open source it for the Web3 community.


# Install

```bash
git clone https://github.com/Quadratic-Labs/Apibara-deserializer.git
cd Apibara-deserializer
pip install .
```
