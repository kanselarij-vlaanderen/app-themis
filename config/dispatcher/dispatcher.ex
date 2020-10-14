defmodule Dispatcher do
  use Matcher

  define_accept_types []

  ###############
  # RESOURCES
  ###############

  get "/catalogs/*path", _ do
    forward conn, path, "http://cache/catalogs"
  end

  get "/datasets/*path", _ do
    forward conn, path, "http://cache/datasets"
  end

  get "/distributions/*path", _ do
    forward conn, path, "http://cache/distributions"
  end

  ###############
  # SPARQL
  ###############
  match "/sparql", %{ layer: :sparql, accept: %{ html: true } } do
    forward conn, [], "http://frontend/sparql"
  end

  match "/sparql", %{ layer: :sparql, accept: %{ sparql: true } } do
    forward conn, [], "http://database:8890/sparql"
  end

  ###############
  # API SERVICES
  ###############
  get "/resource-labels/*path" do
    Proxy.forward conn, path, "http://resource-labels/"
  end

  get "/uri-info/*path" do
    Proxy.forward conn, path, "http://uri-info/"
  end

  #################
  # NOT FOUND
  #################
  match "/*_", %{ last_call: true } do
    send_resp( conn, 404, "Route not found.  See config/dispatcher.ex" )
  end

end
