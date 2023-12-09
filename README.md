# 18755-Project

This project involves the analysis of different networks related to crime data. Follow these steps to set up and run the various components of the project. Orignal dataset can be found [here](https://www.kaggle.com/datasets/cityofLA/crime-in-los-angeles?resource=download).

## Setup Instructions

1. **Download the Data**
   - Download the cleaned dataset from [this link](https://drive.google.com/file/d/1QU3Va8FaeKb32F_WnPTC81i1ckESk6En/view?usp=sharing).
   - Place the downloaded file in the root directory of the project.

2. **Running the Code**
   - Different parts of the project can be executed as described below.

### Temporal Network Analysis

- **Building the Temporal Network and Analysis** (please be aware that this step will take a long time to run)
  ```bash
  cd temporal
  python3 temporal.py
### Age Group Network
- **Building the Network of Age and Area & Visualization Map**
  ```bash
  cd agegroup_area
  python3 age_area_network.py
### Weapon Network
- **Please run the following command before running the code**
  ```bash
  cd weapon
- **Constructing the Crime-Weapon Bipartite Network**
  ```bash
  python3 crime_weapon.py
- **Constructing the Projection Network and Related Analysis**
  ```bash
  python3 crime_weapon_multigraph.py
- **Constructing the Visual Map**
  ```bash
  python3 weapon_visual_map.py