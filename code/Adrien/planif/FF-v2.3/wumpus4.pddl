(define (domain wumpus-4)
  (:requirements :adl :typing)

  ;; object types
  (:types agent wumpus gold arrow square)

  (:predicates
   (adj ?square-1 ?square-2 - square)
   (pit ?square - square)
   (at ?what ?square)
   (have ?who ?what)
   (dead ?who)
  )

  (:action move
    :parameters (?who - agent ?from - square ?to - square)
    :precondition (and (not (dead ?who))
		       (at ?who ?from)
		       (adj ?from ?to)
                        )
    :effect (and (not (at ?who ?from))
		 (at ?who ?to)
		 (when (pit ?to)
		   (dead ?who))
		   (forall (?x - wumpus) (when
		    (and (at ?x ?to)
		    	 (not (dead ?x))) (dead ?who)))
  ))

  (:action take
    :parameters (?who - agent ?where - square ?what)
    :precondition (and (not (dead ?who))
		       (at ?who ?where)
		       (at ?what ?where))
    :effect (and (have ?who ?what)
		 (not (at ?what ?where)))
    )

  (:action shoot
    :parameters (?who - agent ?where - square 
    		 ?with-arrow - arrow ?victim - wumpus 
		 ?where-victim - square)
    :precondition (and (not (dead ?who))
		       (have ?who ?with-arrow)
		       (at ?who ?where)
		       (not (dead ?victim))
		       (at ?victim ?where-victim)
		       (adj ?where ?where-victim)
                       )
    :effect (and (dead ?victim)
		 (not (have ?who ?with-arrow)))
    )
)

