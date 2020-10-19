# median-food-facts



## Data Description

This repository presents a new open-source dataset of general nutritional facts, mainly based on the OpenfoodFacts platform [1]. OpenFoodFacts is a large, raw, community-based database (> referenced 600.000 items) of food products. The data are gathered from general public through a smartphone application. Due to their empirical and community-based nature, these data are subject to noise and result in a low-quality data source. 

This dataset aims to provide more reliable and usable data about general nutritional facts, through cleaning, aggregation and filtering of the original dataset.

File 1 (allmedianfacts.parquet) includes the “raw” dataset, resulting from the extraction of median facts from all items of the OpenFoodFacts dataset.

File 2 (medianfacts.parquet) includes a filtered version of the dataset, keeping only items with at least 5 occurrences in the original data, allowing extraction of a more reliable median value for each characteristic of the table (i.e. each nutritional fact).

## Experimental Design, Materials, and Methods 

The extraction of this dataset from the original data source was obtained through a pipeline of information processing steps, including basic Natural Language Processing (for product disambiguation), statistics and filtering. It was then augmented through automatic web crawling on a generic search engine (StartPage [2]), allowing estimation of the standard weight of common products. The quality of this dataset is hence limited to the current state of the OpenfoodFacts platform (as of 23 January 2020), and to the limited reliability of the automatic text processing of search engine request results.

### Data cleaning, filtering and compression

The original data extracted from the OpenFoodFacts platform are in the form of a large table. This table contains highly redundant information, including a large number of identical values, empty cells or invalid values. Its size can therefore be significantly reduced by filtering useless data, and by using a colum-wise compression method, such as Apache Parquet [3].

The original french nutritional facts dataset was downloaded from the OpenFoodFacts platform, exported as a “csv” file of about 2.2Go - as of 23 January 2020 - accessible here: https://fr.openfoodfacts.org/data/fr.openfoodfacts.org.products.csv . Table 1 indicates statistics about the initial data quality.

 

| Dataset (table) characteristics                         |                 |
| ------------------------------------------------------- | --------------- |
| Nb of lines (food products)                             | 1120758         |
| Nb of columns (variables, including nutritional  facts) | 178             |
| Nb of columns  with > 90% empty values                  | 112 (63%)       |
| Nb of missing values (table cells)                      | 157884457 (79%) |
| Nb of missing energy information (kCal/100g)            | 229799 (20%)    |
| Nb of invalid energy information (> 1000 kCal/100g)     | 1172 (0.1%)     |

Table 1. Characteristics of the original OpenfoodFacts dataset, as of 23 January 2020.

A subset of the original dataset is therefore extracted to keep only relevant data. After data filtering, the dataset comprised 837463 lines, i.e. 75% of the original dataset.

The dataset includes products from various countries worldwide. As the zone of interest for the project is in Belgium, and the language of interest if french, only products from local french-speaking countries (i.e. France, Belgium, and Switzerland) were kept. The resulting dataset comprised 391017 lines, i.e. 35% of the original dataset.

Finally, the file was saved into a parquet file using gzip compression. The final size of the file is about 75Mo.

### Product disambiguation

The products referenced in the OpenFoodFacts platform include various occurrences of identical food items. Each occurrence of an item may differ by the packaging of the product (e.g. bulk and packaged apples, or 50cl vs 6x1,5L of an identical beverage) or by provider brand. Though some products can be manually categorized through the platform, this annotation is of low quality due to the large number of categories (16874 as of 23 January 2020, https://fr.openfoodfacts.org/categories ), and the crowd-sourced nature of the data. To allow proper automatic disambiguation, text mining processes are used to identify identical product, such as synonym and antonym extraction, and removal of stop word (words with low semantic meaning, such as “the”) and any text related to packaging and unit. Plural version of any word are also converted to their singular version. As a result, a product such as “Apples 6-pack 500gr” simply becomes “apple”.

### Usual products extraction

In order to obtain a set of usual products, the number of occurrences for each unique product (after disambiguation) was counted. A threshold is arbitrarily defined to 5 occurrences of an identical name, to consider that product "usual". Based on this threshold, a subset of usual products was extracted from the initial dataset, resulting in 131509 products (i.e. 12% of the original dataset).

### Median dataset extraction

Many nutritional values are given for each product, with more or less consistent values. In order to obtain a robust estimate of the nutritional values for a unique product, a median is calculated on products corresponding to the same name. Median is used as it is known to filter noisy data. The more occurrences in the initial dataset, the more robust estimation of the product median nutritional facts. More usual products are therefore more prone to be more accurately described in this subset.

A median dataset was extracted both the the usual product subset and the unfiltered dataset (including unusual products), resulting respectively in 8470 and 228649 products.

### Data augmentation through web crawling

Generally, recipes indicate an absolute number of ingredients to use  ("take four tomatoes") rather than a total weight. To allow automatic extraction of nutritional facts for any food recipe, information about the unit weight of ingredients is therefore required. This type of information can be considered of the public domain (for a dietitian, a nutritionist or a cooker, it is known that the average - or median- weight of a tomatoe is about 100g). However, there is no exhaustive source indicating the unit weight of any product. A query on a search engine for various products will therefore point to various websites, providing this public-domain information.

In order to provide this information for all products of our dataset, we developed a method for automatically extracting unit weight information from a query on a generic web search engine. From a query with the given keywords: "poids *produit* grammes" (e.g. "poids pomme grammes", meaning in english "weight apple grams"), a web search engine (Startpage was used in the experiment) returns various descriptions, from exerpts of various websites. Ideally, these exerpts are supposed to contains the search information, and therefore they contains ciffers followed a unit (such as g/grams, or kg/kilograms according to the product).

Natural Language Processing (NLP) methods are then used to extract the weights given from various web sources, and a median of the answers is processed on these outputs to extract a more robust estimation of the unit weight of a product. The validity of these data is therefore limited to the (perfectible) performance of the search engine and of the NLP algorithm.

# References

[1] Open food facts - France.
 https://fr.openfoodfacts.org/ , 2020 (accessed 23 January 2020).

[2] Startpage.com – The world’s Most Private Search Engine.
 https://www.startpage.com/ , 2020(accessed 23 January 2020).

[3] Vohra, D. (2016). Apache parquet. In Practical Hadoop Ecosystem (pp. 325-335). Apress, Berkeley, CA.



