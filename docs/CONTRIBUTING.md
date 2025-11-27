# Contributing Guide

Thank you for your interest in contributing to the 1644 EU5 Mod! This guide will teach you step-by-step how to quickly add a new country and see it in-game immediately.

## Table of Contents

1. [Quick Start: Adding a New Country](#quick-start-adding-a-new-country)
2. [How to Edit Characters](#how-to-edit-characters)
3. [Advanced: Using Git to Submit Changes (Optional)](#advanced-using-git-to-submit-changes-optional)

---

## Quick Start: Adding a New Country

Our goal: **Create a new country in 5 minutes and see it in-game!**

### Step 1: Download Project Files (Simplest Method)

You have two options to get the project files:

#### Option 1: Direct ZIP Download (Recommended for Beginners)

1. Open your browser and go to: https://github.com/ProLet-1917/1644
2. Click the green **"Code"** button
3. Select **"Download ZIP"**
4. Extract the ZIP file to any location (e.g., Desktop)
5. Navigate into the extracted `1644` folder

**That's it!** You now have all project files.

#### Option 2: Using Git (If You're Familiar with Git)

```bash
git clone https://github.com/ProLet-1917/1644.git
cd 1644
```

### Step 2: Locate Mod Installation Folder

EU5 mods need to be in a specific folder for the game to recognize them. Find your mod folder:

- **Windows**: `C:\Users\YourUsername\Documents\Paradox Interactive\Europa Universalis V\mod\`
- **Mac**: `~/Documents/Paradox Interactive/Europa Universalis V/mod/`

**Action:**
1. **Copy** or **Move** the `1644` folder to the mod folder above
2. Final path should be: `...Europa Universalis V\mod\1644\`

### Step 3: Edit Country Definition Files

Now let's create your country! You need to edit **two files**:

#### File 1: Country Basic Information

**Location:** `1644\in_game\setup\countries\xxx.txt`

Open this file with Notepad, scroll to the end, and add your country:

```txt
# This is my new country - Example
MYN = {
	color = rgb { 200 50 100 }  # Map color (R=200, G=50, B=100)
	color2 = rgb { 150 30 80 }  # Secondary color
	culture_definition = han_culture  # Culture: Han
	religion_definition = sanjiao  # Religion: Sanjiao
}
```

**Parameter Explanation:**
- `MYN`: Country tag (must be 3 uppercase letters, unique)
- `color`: Map display color, format `rgb { R G B }`, each number 0-255
  - Examples: `rgb { 255 0 0 }` = red, `rgb { 0 255 0 }` = green
- `culture_definition`: Culture type
  - `han_culture` (Han), `jurchen_culture` (Jurchen), `korean_culture` (Korean), etc.
- `religion_definition`: Religion type
  - `sanjiao` (Sanjiao), `mahayana` (Mahayana Buddhism), `shinto` (Shinto), etc.

**Reference Example:**

```1141:1147:in_game/setup/countries/east_asia.txt
MNG = {	#Míng
	color = map_MNG
	color2 = rgb { 179 128 104 }
	culture_definition = han_culture
	religion_definition = sanjiao
	#Released during the Crisis events
}
```

#### File 2: Starting State

**Location:** `1644\main_menu\setup\start\10_countries.txt`

This file defines the country's starting state. Open the file, find the `countries = {` line, and add your country inside these brackets (suggest placing near the end):

```txt
# My new country starting setup
MYN = {
	own_control_core = {
		beijing  # Starting provinces (must match game location names)
	}
	capital = beijing  # Capital
	starting_technology_level = 4  # Starting tech level (1-8)
	country_rank = rank_kingdom  # Country rank
}
```

**Parameter Explanation:**
- `own_control_core`: List of provinces owned at start (one province per line)
  - Common province names: `beijing` (Beijing), `nanjing` (Nanjing), `shenyang` (Shenyang), etc.
- `capital`: Capital location (must be one of the provinces listed above)
- `starting_technology_level`: Starting tech level, recommended 4-5
- `country_rank`: Country rank
  - `rank_county` (County), `rank_duchy` (Duchy), `rank_kingdom` (Kingdom), `rank_empire` (Empire)

**Complete Example:**
```txt
MYN = {
	own_control_core = {
		beijing
		nanjing
		tianjin
	}
	capital = beijing
	starting_technology_level = 4
	country_rank = rank_kingdom
}
```

### Step 4: Save Files

Save both modified files:
- `in_game\setup\countries\east_asia.txt`
- `main_menu\setup\start\10_countries.txt`

Press `Ctrl+S` to save.

### Step 5: Test in Game (Most Important!)

Now for the exciting part - see your country in-game!

1. **Launch Game**: Open Europa Universalis V

2. **Enable Mod**:
   - In the main menu, find **"Mods"** option
   - Make sure **"1644_dev"** mod is checked

4. **Find Your Country**:
   - Find the province location you set on the map
   - **You should see your created country!** 🎉


## How to Edit Characters

Adding characters is similar to adding countries, but you need to understand character data structure.

### File Location

**Character Data File:** `1644\main_menu\setup\start\zzz_05_characters.txt`

### Character Structure Example

Each character follows this format:

```4:21:main_menu/setup/start/zzz_05_characters.txt
# 朱元璋
chi_zhu_yuanzhang = {
	first_name = {
		name = name_yaun2.name_zhang12
	}
	dynasty = rtr_ming_zhu_dynasty
	culture = jianghuai_culture
	religion = sanjiao
	adm = 95
	dip = 95
	mil = 95
	birth_date = 1328.10.21
	birth = zhongli
	death_date = 1398.6.24
	tag = MNG

	ruler_trait = lawgiver
}
```

### Steps to Add a Character

1. **Open Character File**: `main_menu\setup\start\zzz_05_characters.txt`

2. **Find `character_db = {` at the file start**, add your character inside these brackets

3. **Add Your Character at the End** (suggest placing after existing characters):

```txt
# Example Person
chi_example_person = {
	first_name = {
		name = Example_Name
	}
	dynasty = example_dynasty
	culture = han_culture
	religion = sanjiao
	adm = 75
	dip = 80
	mil = 70
	birth_date = 1600.1.1
	birth = beijing
	death_date = 1650.1.1
	tag = MYN  # Country tag (your country code)
	ruler_trait = expansionist
}
```

4. **Save File**

5. **Test in Game**: Launch game, select your country, check if character appears in ruler or general list

### Common Field Descriptions

- **Character ID** (e.g., `chi_example_person`): Unique identifier, suggested format `chi_surname_givenname`
- `first_name`: Name (references localization files, or use English directly)
- `dynasty`: Dynasty name
- `culture`: Character's culture
- `religion`: Character's religion
- `adm`: Administrative ability (0-100)
- `dip`: Diplomatic ability (0-100)
- `mil`: Military ability (0-100)
- `birth_date`: Birth date (format: `YYYY.M.D`, e.g., `1600.1.1`)
- `death_date`: Death date
- `birth`: Birth location (location name)
- `tag`: Country tag (must match your country code)
- `ruler_trait`: Ruler trait
  - `lawgiver`, `conqueror`, `tactical_genius`, `expansionist`, etc.

### ⚠️ Important Rule: Family Order

**Children must be defined AFTER their parents!** Otherwise the game may crash.

✅ **Correct Order:**
```txt
chi_parent = {
	# Parent definition
}

chi_child = {
	father = chi_parent
	# Child definition
}
```

❌ **Wrong Order (Will Cause Crashes):**
```txt
chi_child = {
	father = chi_parent  # Error: parent not defined yet!
}

chi_parent = {
	# Parent definition
}
```

---

## Advanced: Using Git to Submit Changes (Optional)

If you want to share your changes with other players, you can learn to use Git. This section is optional - if you just want to use it yourself, you can skip this.

### Why Use Git?

- Backup your changes
- Collaborate with other contributors
- Merge your contributions into the main project

### Quick Git Guide

#### 1. Install Git

- Download: https://git-scm.com/download/win (Windows) or https://git-scm.com/download/mac (Mac)
- Install: Use default settings

#### 2. Initialize Git in Project Folder

Open Command Prompt/Terminal, navigate to your mod folder:

```bash
cd "C:\Users\YourUsername\Documents\Paradox Interactive\Europa Universalis V\mod\1644"
git init
git remote add origin https://github.com/ProLet-1917/1644.git
git pull origin main
```

#### 3. Commit Your Changes

```bash
# See which files you modified
git status

# Add modified files
git add in_game/setup/countries/east_asia.txt
git add main_menu/setup/start/10_countries.txt

# Commit changes
git commit -m "Add new country MYN"

# Push to GitHub (need to fork project first)
git push
```

#### 4. Create Pull Request

1. Go to: https://github.com/ProLet-1917/1644
2. Click "Fork" to create your copy
3. Push your changes to your fork
4. Click "New Pull Request"
5. Fill in description, wait for review

**Tip:** Git workflow can be complex. If you encounter difficulties, you can:
- Create an Issue on GitHub to ask
- Look up Git tutorials
- Or use it yourself first, learn Git later

---

## Frequently Asked Questions

### My Country Doesn't Appear in Game

- Check if files are saved
- Confirm country tag is unique (no duplicates)
- Check for syntax errors (bracket pairing)
- Check error log

### Provinces Display Incorrectly

- Confirm province names are correct (case-sensitive)
- Check if provinces exist in-game

### Game Crashes

- Check error log
- Check for syntax errors
- Confirm character definition order is correct (children after parents)

### How to Modify Existing Countries?

Find the corresponding country tag (e.g., `MNG`), directly modify properties. Remember to save and test in-game.

---

## Need Help?

- **Having Issues?** Create an Issue on GitHub: https://github.com/ProLet-1917/1644/issues
- **Not Sure How?** Look at existing country and character definitions in the project as reference
- **Want More Features?** Check EU5 modding documentation: https://eu5.paradoxwikis.com/

**Happy Modding!** 🎮
