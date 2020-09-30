(in-package :mu-cl-resources)

(defparameter *supply-cache-headers-p* t)

(read-domain-file "catalog.lisp")
(read-domain-file "dataset.lisp")
(read-domain-file "distribution.lisp")

