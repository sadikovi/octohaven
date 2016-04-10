# Job class to render the whole content segment
content = [
  {id: "spark-status", name: "Spark status", api: "GET /spark/status", desc:
    "Show current Spark cluster status, can be 0 (free), -1 (busy), -2 (not available)"},
  {id: "finder-home", name: "Finder (root)", api: "GET /finder/home", desc:
    "Traverse root directory and list folders and files in root"},
  {id: "finder-dir", name: "Finder (directory)", api: "GET /finder/home/<path:rel_path>", desc:
    "Traverse directory and list folders and files in directory, e.g. /finder/home/foo/bar will " +
    "list folders and files in directory bar"},
  {id: "job-list", name: "List jobs", api: "GET /job/list?status=#", desc:
    "List all jobs for provided status that can be one of #{STATUS_LIST}"},
  {id: "job-get", name: "Get job information", api: "GET /job/get/<int:uid>", desc:
    "Get information for a job with specified uid"},
  {id: "job-create", name: "Create job", api: "POST /job/create"
    , desc: "Create job, requires data in JSON format", code: """
      {
        "name": "Friendly job name",
        "entrypoint": "com.foo.bar.MainClass",
        "dmemory": "4g",
        "ememory": "4g",
        "options": "spark.files.overwrite=true spark.sql.shuffle.partitions=250",
        "jobconf": "foo bar",
        "delay": 0,
        "jar": "/full/path/to/jar/file"
      }
    """},
  {id: "template-list", name: "List templates", api: "GET /template/list", desc:
    "List all created templates"},
  {id: "timetable-list", name: "List timetables", api: "GET /timetable/list?status=#", desc:
    "List all timetables for provided status that can be one of #{TIMETABLE_STATUSES}"},
  {id: "timetable-get", name: "Get timetable information", api: "GET /timetable/get/<int:uid>", desc:
    "Get information for a timetable with specified uid"},
  {id: "timetable-pause", name: "Pause timetable", api: "GET /timetable/pause/<int:uid>", desc:
    "Pause timetable with specified uid"},
  {id: "timetable-resume", name: "Resume timetable", api: "GET /timetable/resume/<int:uid>", desc:
    "Resume timetable with specified uid"}
]

class ApiView extends Reactable
  render: ->
    @div({className: "segments"},
      (ApiEntry.new(key: x.id, id: x.id, name: x.name, api: x.api, desc: x.desc, code: x.code) \
        for x in @props.content)
    )

class ApiEntry extends Reactable
  render: ->
    @div({className: "segment"},
      @h3({id: "#{@props.id}"}, "#{@props.name}"),
      @div({className: "text-mono"}, "#{@props.api}"),
      @p({className: "text-mute"}, "#{@props.desc}"),
      if @props.code
        @pre({}, "#{@props.code}")
      else
        null
    )

class ApiLinks extends Reactable
  render: ->
    @nav({className: "menu"},
      (ApiLink.new(key: x.id, link: "##{x.id}", name: x.name) for x in @props.content)
    )

class ApiLink extends Reactable
  render: ->
    @a({className: "menu-item", href: "#{@props.link}"}, "#{@props.name}")

ReactDOM.render ApiView.new(content: content), document.getElementById("content")
ReactDOM.render ApiLinks.new(content: content), document.getElementById("api-links")
