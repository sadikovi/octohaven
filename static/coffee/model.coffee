# generic dictionary object
class Dictionary
    constructor: (@settings = {}) -> @correct(@settings)

    set: (key, value) -> if value != null then @settings[key] = value.toString() else null

    getOrElse: (key, alternative) -> if key of @settings then @settings[key] else alternative

    get: (key) -> @getOrElse(key, null)

    exists: (key) -> @get(key) != null

    correct: -> @set(key, value) for key, value of @settings

# template for a job, keeps only key - value pairs, where value is always a string
class Template extends Dictionary
@Template ?= Template

# timetable, keeps only key - value pairs, where value is always a string
class Timetable extends Dictionary
@Timetable ?= Timetable

# cluster status, has keys such as master address, ui address and status
class ClusterStatus extends Dictionary
@ClusterStatus ?= ClusterStatus
