(define-resource dataset ()
   :class (s-prefix "dcat:Dataset")
   :properties `((:title :string ,(s-prefix "dct:title"))
                 (:description :string ,(s-prefix "dct:description")))
   :has-one `((catalog :via ,(s-prefix "dcat:dataset")
                       :inverse t
                       :as "catalog"))
   :resource-base (s-url "http://public-api/datasets/")
   :on-path "datasets")