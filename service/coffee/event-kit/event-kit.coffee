###
exports.Emitter = require './emitter'
exports.Disposable = require './disposable'
exports.CompositeDisposable = require './composite-disposable'
###
@eventkit = {}

# Essential: A handle to a resource that can be disposed. For example,
# {Emitter::on} returns disposables representing subscriptions.
# module.exports =
class Disposable
  disposed: false

  ###
  Section: Construction and Destruction
  ###

  # Public: Construct a Disposable
  #
  # * `disposalAction` An action to perform when {::dispose} is called for the
  #   first time.
  constructor: (@disposalAction) ->

  # Public: Perform the disposal action, indicating that the resource associated
  # with this disposable is no longer needed.
  #
  # You can call this method more than once, but the disposal action will only
  # be performed the first time.
  dispose: ->
    unless @disposed
      @disposed = true
      @disposalAction?()
      @disposalAction = null
    return


# Essential: An object that aggregates multiple {Disposable} instances together
# into a single disposable, so they can all be disposed as a group.
#
# These are very useful when subscribing to multiple events.
#
# ## Examples
#
# ```coffee
# {CompositeDisposable} = require 'atom'
#
# class Something
#   constructor: ->
#     @disposables = new CompositeDisposable
#     editor = atom.workspace.getActiveTextEditor()
#     @disposables.add editor.onDidChange ->
#     @disposables.add editor.onDidChangePath ->
#
#   destroy: ->
#     @disposables.dispose()
# ```
# module.exports =
class CompositeDisposable
  disposed: false

  ###
  Section: Construction and Destruction
  ###

  # Public: Construct an instance, optionally with one or more disposables
  constructor: ->
    @disposables = new Set
    @add(disposable) for disposable in arguments

  # Public: Dispose all disposables added to this composite disposable.
  #
  # If this object has already been disposed, this method has no effect.
  dispose: ->
    unless @disposed
      @disposed = true
      @disposables.forEach (disposable) ->
        disposable.dispose()
      @disposables = null
    return

  ###
  Section: Managing Disposables
  ###

  # Public: Add a disposable to be disposed when the composite is disposed.
  #
  # If this object has already been disposed, this method has no effect.
  #
  # * `disposable` {Disposable} instance or any object with a `.dispose()`
  #   method.
  add: ->
    unless @disposed
      @disposables.add(disposable) for disposable in arguments
    return

  # Public: Remove a previously added disposable.
  #
  # * `disposable` {Disposable} instance or any object with a `.dispose()`
  #   method.
  remove: (disposable) ->
    @disposables.delete(disposable) unless @disposed
    return

  # Public: Clear all disposables. They will not be disposed by the next call
  # to dispose.
  clear: ->
    @disposables.clear() unless @disposed
    return


class Emitter
  isDisposed: false

  ###
  Section: Construction and Destruction
  ###

  # Public: Construct an emitter.
  #
  # ```coffee
  # @emitter = new Emitter()
  # ```
  constructor: ->
    @handlersByEventName = {}

  # Public: Unsubscribe all handlers.
  dispose: ->
    @handlersByEventName = null
    @isDisposed = true

  ###
  Section: Event Subscription
  ###

  # Public: Register the given handler function to be invoked whenever events by
  # the given name are emitted via {::emit}.
  #
  # * `eventName` {String} naming the event that you want to invoke the handler
  #   when emitted.
  # * `handler` {Function} to invoke when {::emit} is called with the given
  #   event name.
  #
  # Returns a {Disposable} on which `.dispose()` can be called to unsubscribe.
  on: (eventName, handler, unshift=false) ->
    if @isDisposed
      throw new Error("Emitter has been disposed")

    if typeof handler isnt 'function'
      throw new Error("Handler must be a function")

    if currentHandlers = @handlersByEventName[eventName]
      if unshift
        @handlersByEventName[eventName] = [handler].concat(currentHandlers)
      else
        @handlersByEventName[eventName] = currentHandlers.concat(handler)
    else
      @handlersByEventName[eventName] = [handler]

    new Disposable(@off.bind(this, eventName, handler))

  # Public: Register the given handler function to be invoked *before* all
  # other handlers existing at the time of subscription whenever events by the
  # given name are emitted via {::emit}.
  #
  # Use this method when you need to be the first to handle a given event. This
  # could be required when a data structure in a parent object needs to be
  # updated before third-party event handlers registered on a child object via a
  # public API are invoked. Your handler could itself be preempted via
  # subsequent calls to this method, but this can be controlled by keeping
  # methods based on `::preempt` private.
  #
  # * `eventName` {String} naming the event that you want to invoke the handler
  #   when emitted.
  # * `handler` {Function} to invoke when {::emit} is called with the given
  #   event name.
  #
  # Returns a {Disposable} on which `.dispose()` can be called to unsubscribe.
  preempt: (eventName, handler) ->
    @on(eventName, handler, true)

  # Private: Used by the disposable.
  off: (eventName, handlerToRemove) ->
    return if @isDisposed

    if oldHandlers = @handlersByEventName[eventName]
      newHandlers = []
      for handler in oldHandlers when handler isnt handlerToRemove
        newHandlers.push(handler)
      @handlersByEventName[eventName] = newHandlers
    return

  ###
  Section: Event Emission
  ###

  # Public: Invoke handlers registered via {::on} for the given event name.
  #
  # * `eventName` The name of the event to emit. Handlers registered with {::on}
  #   for the same name will be invoked.
  # * `value` Callbacks will be invoked with this value as an argument.
  emit: (eventName, value) ->
    if handlers = @handlersByEventName?[eventName]
      handler(value) for handler in handlers
    return

#################
# Export
#################
@eventkit.Disposable ?= Disposable
@eventkit.CompositeDisposable ?= CompositeDisposable
@eventkit.Emmitter ?= Emitter
