defmodule Dispatcher do
  use Matcher

  define_accept_types []

  get "/catalogs/*path", _ do
    forward conn, path, "http://cache/catalogs"
  end

  get "/datasets/*path", _ do
    forward conn, path, "http://cache/datasets"
  end

  get "/distributions/*path", _ do
    forward conn, path, "http://cache/distributions"
  end

  match "/*_", %{ last_call: true } do
    send_resp( conn, 404, "Route not found.  See config/dispatcher.ex" )
  end

end
