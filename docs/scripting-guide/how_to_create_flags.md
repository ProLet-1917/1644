# How to Create Flags in EU5 Mod

## File Locations

- **Coat of Arms**: `main_menu/common/coat_of_arms/coat_of_arms/*.txt`
- **Flag Definitions**: `main_menu/common/flag_definitions/*.txt`
- **Country Setup**: `main_menu/setup/start/10_countries.txt`
- **Graphics**: `main_menu/gfx/coat_of_arms/colored_emblems/*.dds` (768x512 pixels)


## Steps to Set Flag for a Country

### Step 1: Define Coat of Arms (COA)

Create or edit a .txt file in `main_menu/common/coat_of_arms/coat_of_arms/`:

TAG = {  # Country tag (e.g., CSH, CXI)
    pattern = "pattern_solid.dds"          # Background pattern
    color1 = "red"                         # Primary color
    color2 = "white"                       # Secondary color
    
    Graphics find in: `main_menu/gfx/coat_of_arms/colored_emblems/*.dds` (768x512 pixels)
    colored_emblem = {
        texture = "ce_roundel.dds"         # Emblem texture
        color1 = "white"
        instance = { position = { 0.5 0.5 } scale = { 0.8 0.8 } }
    }
}
```

### Step 2: Define Flag Definition

Create or edit a .txt file in `main_menu/common/flag_definitions/`:

```txt
TAG = {
    flag_definition = {
        coa = TAG                         # References the COA from Step 1
        subject_canton = TAG              # Canton for subject countries
        allow_overlord_canton = yes       # Allow overlord to add canton
        priority = 1                      # Higher = takes precedence
    }
}
```

### Step 3: Reference Flag in Country Setup

Edit the country definition in `main_menu/setup/start/10_countries.txt`:

```txt
TAG = {
    # ... other country settings ...
    flag = "TAG"                          # Must match the country tag
    country_name = "TAG"
    # ... other country settings ...
}
```

## Notes

- The `coa` parameter in flag_definition must match the COA key (country tag)
- The `flag` parameter in country setup must match the country tag
- Higher priority flags take precedence when multiple definitions exist
- Use `trigger = {}` for conditional flags (government type, date, etc.)

