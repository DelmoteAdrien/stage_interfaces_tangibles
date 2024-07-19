(define (domain configuration)
  (:requirements :adl :typing :conditional-effects :strips )

  ;; object types
  (:types 
  
  squareval
  squareval1 squareval2  - squareval
  squareval11 squareval12 - squareval1
  squareval21 squareval22 squareval23 - squareval2
  
  squarevar
  squarevar1 squarevar2 - squarevar
  
  squaretheme
  
  objetval objetvar objettheme )



  (:predicates
   (at ?objet ?where )
   (istake)
   (take ?objet)
   (selectedvar ?var )
   (selectedtheme ?theme)
  )



  (:action putval11
    :parameters (?what - objetval ?to - squareval11 )
    :precondition (and 	
    			(take ?what)
    			(selectedvar sqvar-11 )
    	
    				
    		  )
    :effect (and (not (istake))
		 (at ?what ?to)
		 (not (take ?what))
		 
  ))
  
  
    (:action putval12
    :parameters (?what - objetval ?to - squareval12 )
    :precondition (and 	
    			(take ?what)
    			(selectedvar sqvar-12 )
    		
    			
    		  )
    :effect (and (not (istake))
		 (at ?what ?to)
		 (not (take ?what))
			
  ))
  
    (:action putval21
    :parameters (?what - objetval ?to - squareval21 )
    :precondition (and 	
    			(take ?what)
    			(selectedvar sqvar-21 )
    			
    			
    		  )
    :effect (and (not (istake))
		 (at ?what ?to)
		 (not (take ?what))
			
  ))
  
    (:action putval22
    :parameters (?what - objetval ?to - squareval22 )
    :precondition (and 	
    			(take ?what)
    			(selectedvar sqvar-22 )
    		
    			
    		  )
    :effect (and (not (istake))
		 (at ?what ?to)
		 (not (take ?what))
			
  ))
  
     (:action putval23
    :parameters (?what - objetval ?to - squareval23 )
    :precondition (and 	
    			(take ?what)
    			(selectedvar sqvar-23 )
    		
    			
    		  )
    :effect (and (not (istake))
		 (at ?what ?to)
		 (not (take ?what))
			
  ))
  
  
  
    (:action putvar1
    :parameters (?what - objetvar ?to - squarevar1)
    :precondition (and 
    			(take ?what)
    			(selectedtheme sqtheme-1)
    			
    		  )
    :effect (and (not (istake))
		 (at ?what ?to)
		 (not (take ?what))
		 (selectedvar ?to)
		 
  ))
  
    (:action putvar2
    :parameters (?what - objetvar ?to - squarevar2)
    :precondition (and 
    			(take ?what)
    			(selectedtheme sqtheme-2)
    			
    		  )
    :effect (and (not (istake))
		 (at ?what ?to)
		 (not (take ?what))
		 (selectedvar ?to)
		 
  ))
  
  
  
  
  
   (:action puttheme
    :parameters (?what - objettheme ?to - squaretheme)
    :precondition (and 
    			(take ?what)
    		  )
    :effect (and 
    		(not (istake))
		(at ?what ?to)
		(not (take ?what))
		(selectedtheme ?to)
	
  ))


  
  (:action take
    :parameters (?what  ?from )
    :precondition (and 
    			(at ?what ?from)
    			(not(istake))
    		  ) 
    :effect (and 
    		(not(at ?what ?from))
		(istake)
		(take ?what)
		(not(selectedvar ?from ))
		(not(selectedtheme ?from ))
	    )
    )
 )
