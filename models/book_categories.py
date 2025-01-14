from enum import StrEnum


class BookCategory(StrEnum):
    # Fiction
    ADVENTURE = "adventure"
    CLASSICS = "classics"
    CONTEMPORARY = "contemporary"
    FANTASY = "fantasy"
    HISTORICAL_FICTION = "historicalFiction"
    HORROR = "horror"
    MYSTERY_CRIME = "mysteryCrime"
    ROMANCE = "romance"
    SCIENCE_FICTION = "scienceFiction"
    THRILLER_SUSPENSE = "thrillerSuspense"
    YOUNG_ADULT = "youngAdult"

    # Non-Fiction
    ART_PHOTOGRAPHY = "artPhotography"
    BIOGRAPHY_MEMOIR = "biographyMemoir"
    BUSINESS_ECONOMICS = "businessEconomics"
    COOKING_FOOD = "cookingFood"
    HEALTH_WELLNESS = "healthWellness"
    HISTORY = "history"
    POLITICS_SOCIAL_SCIENCES = "politicsSocialSciences"
    RELIGION_SPIRITUALITY = "religionSpirituality"
    SCIENCE_NATURE = "scienceNature"
    SELF_HELP = "selfHelp"
    TRAVEL_ADVENTURE = "travelAdventure"

    # Academic & Educational
    COMPUTERS_TECHNOLOGY = "computersTechnology"
    ENGINEERING = "engineering"
    MATHEMATICS = "mathematics"
    MEDICAL_HEALTH_SCIENCES = "medicalHealthSciences"
    PSYCHOLOGY = "psychology"
    REFERENCE = "reference"
    STUDY_AIDS = "studyAids"
    TEST_PREPARATION = "testPreparation"
    TEXTBOOKS = "textbooks"

    # Children's Books
    ACTIVITY_BOOKS = "activityBooks"
    EARLY_LEARNING = "earlyLearning"
    PICTURE_BOOKS = "pictureBooks"
    CHAPTER_BOOKS = "chapterBooks"
    MIDDLE_GRADE = "middleGrade"

    # Comics & Graphic Novels
    MANGA = "manga"
    SUPERHEROES = "superheroes"
    WEBCOMICS = "webcomics"
    FANTASY_SCIFI = "fantasySciFi"

    # Genres for Special Audiences
    LGBTQ = "lgbtq"
    MULTICULTURAL = "multicultural"
    WOMENS_FICTION = "womensFiction"

    # Other Genres
    POETRY = "poetry"
    DRAMA = "drama"
    ESSAYS = "essays"
    ANTHOLOGIES = "anthologies"
