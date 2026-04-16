;;;;;;;;;;;;;;;;;;;
;;; Backend
;;;;;;;;;;;;;;;;;;;

(in-package :client)
(setf *backend* "http://triplestore:8890/sparql")

;;;;;;;;;;;;;;;;;;;
;;; Delta
;;;;;;;;;;;;;;;;;;;

(in-package :delta-messenger)
(add-delta-messenger "http://delta-notifier/")

;;;;;;;;;;;;;;;;;;;
;;; ACL
;;;;;;;;;;;;;;;;;;;

(in-package :acl)

(define-prefixes
  :foaf "http://xmlns.com/foaf/0.1/"
  :dcat "http://www.w3.org/ns/dcat#"
  :skos "http://www.w3.org/2004/02/skos/core#"
  :person "http://www.w3.org/ns/person#"
  :mandaat "http://data.vlaanderen.be/ns/mandaat#"
  :org "http://www.w3.org/ns/org#"
  :besluit "http://data.vlaanderen.be/ns/besluit#"
  :nfo "http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#"
  :dossier "https://data.vlaanderen.be/ns/dossier#")

(supply-allowed-group "public")

(supply-allowed-group "clean")

(define-graph public ("http://mu.semte.ch/graphs/public")
  ("foaf:Agent" -> _)
  ("dcat:Catalog" -> _)
  ("dcat:Dataset" -> _)
  ("dcat:Distribution" -> _)
  ("skos:ConceptScheme" -> _)
  ("skos:Concept" -> _)
  ("person:Person" -> _)
  ("mandaat:Mandataris" -> _)
  ("mandaat:Mandaat" -> _)
  ("org:Role" -> _)
  ("besluit:Bestuursorgaan" -> _)
  ("besluit:Bestuurseenheid" -> _)
  ("besluit:Vergaderactiviteit" -> _)
  ("nfo:FileDataObject" -> _)
  ("dossier:Stuk" -> _))

(define-graph clean ("http://mu.semte.ch/application")
  ("foaf:Agent" -> _)
  ("dcat:Catalog" -> _)
  ("dcat:Dataset" -> _)
  ("dcat:Distribution" -> _)
  ("skos:ConceptScheme" -> _)
  ("skos:Concept" -> _)
  ("person:Person" -> _)
  ("mandaat:Mandataris" -> _)
  ("mandaat:Mandaat" -> _)
  ("org:Role" -> _)
  ("besluit:Bestuursorgaan" -> _)
  ("besluit:Bestuurseenheid" -> _)
  ("besluit:Vergaderactiviteit" -> _)
  ("nfo:FileDataObject" -> _)
  ("dossier:Stuk" -> _))

(grant (read)
  :to-graph public
  :for-allowed-group "public")

(grant (write)
  :to-graph clean
  :for-allowed-group "clean")
