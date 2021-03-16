alias Acl.Accessibility.Always, as: AlwaysAccessible
alias Acl.Accessibility.ByQuery, as: AccessByQuery
alias Acl.GraphSpec.Constraint.Resource.AllPredicates, as: AllPredicates
alias Acl.GraphSpec.Constraint.Resource.NoPredicates, as: NoPredicates
alias Acl.GraphSpec.Constraint.ResourceFormat, as: ResourceFormatConstraint
alias Acl.GraphSpec.Constraint.Resource, as: ResourceConstraint
alias Acl.GraphSpec, as: GraphSpec
alias Acl.GroupSpec, as: GroupSpec
alias Acl.GroupSpec.GraphCleanup, as: GraphCleanup

defmodule Acl.UserGroups.Config do

  def user_groups do
    [
      %GroupSpec{
        name: "public",
        useage: [:read],
        access: %AlwaysAccessible{},
        graphs: [ %GraphSpec{
          graph: "http://mu.semte.ch/graphs/public",
          constraint: %ResourceConstraint{
            resource_types: [
              "http://xmlns.com/foaf/0.1/Agent",
              "http://www.w3.org/ns/dcat#Catalog",
              "http://www.w3.org/ns/dcat#Dataset",
              "http://www.w3.org/ns/dcat#Distribution",
              "http://www.w3.org/2004/02/skos/core#ConceptScheme",
              "http://www.w3.org/2004/02/skos/core#Concept",
              "http://www.w3.org/ns/person#Person",
              "http://data.vlaanderen.be/ns/mandaat#Mandataris",
              "http://data.vlaanderen.be/ns/mandaat#Mandaat",
              "http://www.w3.org/ns/org#Role",
              "http://data.vlaanderen.be/ns/besluit#Bestuursorgaan",
              "http://data.vlaanderen.be/ns/besluit#Bestuurseenheid",
              "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#FileDataObject"
            ] } } ]
      },

      # // CLEANUP
      #
      %GraphCleanup{
        originating_graph: "http://mu.semte.ch/application",
        useage: [:write],
        name: "clean"
      }
    ]
  end
end
