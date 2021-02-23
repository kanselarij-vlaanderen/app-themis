defmodule Dispatcher do
  use Matcher

  define_accept_types [
    json: [ "application/json", "application/vnd.api+json" ],
    html: [ "text/html", "application/xhtml+html" ],
    sparql: [ "application/sparql-results+json" ],
    any: [ "*/*" ]
  ]

  define_layers [ :static, :sparql, :resources, :api_services, :frontend_fallback, :not_found ]

  options "/*_path", _ do
    conn
    |> Plug.Conn.put_resp_header( "access-control-allow-headers", "content-type,accept" )
    |> Plug.Conn.put_resp_header( "access-control-allow-methods", "*" )
    |> send_resp( 200, "{ \"message\": \"ok\" }" )
  end

  ###############
  # STATIC
  ###############
  get "/assets/*path", %{ layer: :static } do
    forward conn, path, "http://frontend/assets/"
  end

  get "/index.html", %{ layer: :static } do
    forward conn, [], "http://frontend/index.html"
  end

  get "/favicon.ico", %{ layer: :static } do
    send_resp( conn, 404, "" )
  end

  ###############
  # SPARQL
  ###############
  get "/sparql", %{ layer: :sparql, accept: %{ html: true } } do
    forward conn, [], "http://frontend/sparql"
  end

  match "/sparql", %{ layer: :sparql, accept: %{ sparql: true } } do
    forward conn, [], "http://database:8890/sparql"
  end

  ###############
  # RESOURCES
  ###############

  get "/catalogs/*path", %{ layer: :resources, accept: %{ json: true } } do
    forward conn, path, "http://cache/catalogs/"
  end

  get "/datasets/*path", %{ layer: :resources, accept: %{ json: true } } do
    forward conn, path, "http://cache/datasets/"
  end

  get "/distributions/*path", %{ layer: :resources, accept: %{ json: true } } do
    forward conn, path, "http://cache/distributions/"
  end

  get "/persons/*path", %{ layer: :resources, accept: %{ json: true } } do
    forward conn, path, "http://cache/persons/"
  end

  get "/mandatees/*path", %{ layer: :resources, accept: %{ json: true } } do
    forward conn, path, "http://cache/mandatees/"
  end

  get "/mandates/*path", %{ layer: :resources, accept: %{ json: true } } do
    forward conn, path, "http://cache/mandates/"
  end

  get "/government-functions/*path", %{ layer: :resources, accept: %{ json: true } } do
    forward conn, path, "http://cache/government-functions/"
  end

  get "/government-bodies/*path", %{ layer: :resources, accept: %{ json: true } } do
    forward conn, path, "http://cache/government-bodies/"
  end

  get "/government-units/*path", %{ layer: :resources, accept: %{ json: true } } do
    forward conn, path, "http://cache/government-units/"
  end

  ###############
  # API SERVICES
  ###############
  get "/resource-labels/*path", %{ layer: :api_services, accept: %{ json: true } } do
    forward conn, path, "http://resource-labels-cache/"
  end

  get "/uri-info/*path", %{ layer: :api_services, accept: %{ json: true } } do
    forward conn, path, "http://uri-info/"
  end

  get "/files/*path", %{ layer: :api_services, accept: %{ any: true } } do
    forward conn, path, "http://file/files/"
  end

  #################
  # FRONTEND PAGES
  #################
  get "/*path", %{ layer: :frontend_fallback, accept: %{ html: true } } do
    # We forward path for fastboot
    forward conn, path, "http://frontend/"
  end

  #################
  # NOT FOUND
  #################
  match "/*_", %{ last_call: true } do
    send_resp( conn, 404, "Route not found.  See config/dispatcher.ex" )
  end

end
