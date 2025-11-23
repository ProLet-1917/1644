# How to Create Flags in EU5 Mod

## Overview

Flags in Europa Universalis V are defined through flag definitions and coat of arms (COA) files. This guide provides a brief introduction to creating custom flags for your mod.

## File Structure

### 1. Flag Definitions
Flags are defined in:
- **Location**: `main_menu/common/flag_definitions/`
- **Format**: `.txt` files containing flag definition blocks

### 2. Coat of Arms Assets
Flag graphics are stored in:
- **Location**: `main_menu/gfx/coat_of_arms/`
- **Subdirectories**:
  - `colored_emblems/` - Colored emblem files (.dds format)
  - `patterns/` - Pattern templates (.dds format)
  - `textured_emblems/` - Textured emblem files (.dds format)

## Basic Flag Definition Syntax

```txt
TAG = {  # Country tag (e.g., ENG, FRA)
    flag_definition = {
        coa = COA_KEY                    # Main flag/coat of arms
        subject_canton = COA_KEY         # Canton for subjects
        allow_overlord_canton = yes      # Allow overlord to add canton
        coa_with_overlord_canton = COA_KEY  # Flag when overlord canton is applied
        priority = 1                     # Higher priority = takes precedence
        trigger = {                      # Conditions for this flag
            # trigger conditions
        }
    }
}
```

## Key Components

### CoA (Coat of Arms)
- The `coa` parameter specifies which coat of arms to use
- Can reference a single COA or a list: `coa = list "template_name_list"`
- COA keys typically match the country tag or use descriptive names

### Priorities
- Higher priority values take precedence
- Default colonial flags often use priority 500
- Special flags can use priorities up to 9500+

### Triggers
Flags can change based on game conditions:
- Government type (monarchy, republic, etc.)
- Date periods
- Religion
- Regional/cultural triggers
- Special events or variables

## Steps to Create a Custom Flag

1. **Create the COA graphics** (if needed)
   - Design your flag as a `.dds` file
   - Standard dimensions: 768x512 pixels
   - Save to `main_menu/gfx/coat_of_arms/colored_emblems/`

2. **Define the flag in a definition file**
   - Create or edit a file in `main_menu/common/flag_definitions/`
   - Add your country tag block with flag definitions

3. **Test in-game**
   - Load your mod
   - Verify the flag appears correctly for your country

## Example

```txt
CUS = {  # Custom country tag
    flag_definition = {
        coa = CUS
        subject_canton = CUS
        allow_overlord_canton = yes
        priority = 1
    }
    flag_definition = {
        coa = CUS_monarchy
        subject_canton = CUS
        priority = 100
        trigger = {
            coa_def_monarchy_trigger = yes
        }
    }
}
```

## Color Codes Reference

Common heraldic tincture codes:
- **A** - Argent (White)
- **O** - Or (Yellow)
- **B** - Azure (Blue)
- **G** - Gules (Red)
- **S** - Sable (Black)
- **V** - Vert/Sinople (Green)
- **P** - Purple/Pourpre
- **M** - Brown/Maroon

## Additional Notes

- Use the `DEFAULT` list for general flag definitions
- Colonial flags automatically inherit overlord cantons if `allow_overlord_canton = yes`
- Multiple flag definitions can exist for the same country with different triggers
- The highest priority valid flag (based on triggers) will be used

## Resources

- Original game files: `E:\SteamLibrary\steamapps\common\Europa Universalis V\game\main_menu\common\flag_definitions\00_flag_definitions.txt`
- Pattern templates: `main_menu/gfx/coat_of_arms/patterns/`
- Colored emblems: `main_menu/gfx/coat_of_arms/colored_emblems/`

