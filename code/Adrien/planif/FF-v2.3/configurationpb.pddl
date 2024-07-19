(define (problem configuration)
  (:domain configuration)

  (:objects
   sqval-init 
   sqvar-init 
   
   sqval-111 sqval-112 sqval-113 sqval-114 sqval-115 sqval-116 - squareval11
   sqval-121 sqval-122 sqval-123 sqval-124 sqval-125 sqval-126 - squareval12
   
   sqval-211 sqval-212 sqval-213 - squareval21 
   sqval-221 sqval-222 sqval-223 - squareval22 
   sqval-231 sqval-232 sqval-233 - squareval23
   
   
   sqvar-11 sqvar-12 - squarevar1
   sqvar-21 sqvar-22 sqvar-23 - squarevar2
   
   
   sqtheme-1 sqtheme-2 sqtheme-init - squaretheme
   
   objetval-1 - objetval
   objetvar-1 - objetvar
   objettheme-1 - objettheme
  )
  
  (:init 
	 (at objetval-1 sqval-init) (at objetvar-1 sqvar-init ) (at objettheme-1 sqtheme-init )
   )

  (:goal (and 
  		(at objetval-1 sqval-231) 
  	     )
  )
)
