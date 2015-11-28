# generic dictionary object
class Dictionary
    constructor: (@settings = {}) -> @correct(@settings)

    set: (key, value) -> if value != null then @settings[key] = value.toString() else null

    get: (key) -> if key of @settings then @settings[key] else null

    exists: (key) -> @get(key) != null

    correct: -> @set(key, value) for key, value of @settings

# template for a job, keeps only key - value pairs, where value is always a string
class Template extends Dictionary
@Template ?= Template

# timetable, keeps only key - value pairs, where value is always a string
class Timetable extends Dictionary
@Timetable ?= Timetable
