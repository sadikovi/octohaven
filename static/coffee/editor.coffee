form = document.getElementById "octohaven-editor-form"
unless form
    throw new Error "Form is undefined"

canvas = new @Canvas form
console.log canvas
# add new action
add = new @Control "+ module", (itself) ->
    console.log itself
del = new @Control "- module", (itself) ->
    console.log itself

canvas.addControl add
canvas.addControl del
