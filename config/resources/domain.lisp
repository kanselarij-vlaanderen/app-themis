(in-package :mu-cl-resources)

(defparameter *supply-cache-headers-p* t
  "when non-nil, cache headers are supplied.  this works together with mu-cache.")
(setf *cache-model-properties-p* t)
(defparameter *include-count-in-paginated-responses* t
  "when non-nil, all paginated listings will contain the number
   of responses in the result object's meta.")
(defparameter *cache-count-queries* t)
(defparameter *cache-model-properties* t)
(setf sparql:*experimental-no-application-graph-for-sudo-select-queries* t)

(defparameter *max-group-sorted-properties* t)

(read-domain-file "dcat.json")
(read-domain-file "besluitvorming.json")
(read-domain-file "email-domain.lisp")
(read-domain-file "health-check.lisp")

(defcall :get (base-path)
  (handler-case
      (progn
        (verify-json-api-request-accept-header)
        (list-call (find-resource-by-path base-path)))
    (no-such-resource ()
      (respond-not-found))
    (access-denied (condition)
      (response-for-access-denied-condition condition))
    (no-such-link (condition)
      (respond-not-acceptable (jsown:new-js
                                  ("errors" (jsown:new-js ("title" "Request invalid"))))))
    (no-such-property (condition)
      (let ((message
             (format nil "Could not find property (~A) on resource (~A)."
                     (path condition) (json-type (resource condition)))))
        (respond-not-acceptable (jsown:new-js
                                  ("errors" (jsown:new-js
                                              ("title" message)))))))
    (cl-fuseki:sesame-exception (exception)
      (declare (ignore exception))
      (respond-server-error
       (jsown:new-js
         ("errors" (jsown:new-js
                     ("title" (s+ "Could not execute SPARQL query.")))))))
    (configuration-error (condition)
      (respond-server-error
       (jsown:new-js
         ("errors" (jsown:new-js
                     ("title" (s+ "Server configuration issue: " (description condition))))))))
    (incorrect-accept-header (condition)
      (respond-not-acceptable (jsown:new-js
                                ("errors" (jsown:new-js
                                           ("title" (description condition)))))))
    (error (condition)
      (respond-general-server-error))))

