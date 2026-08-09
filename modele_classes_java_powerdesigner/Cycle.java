package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "cycles")
public class Cycle {
    @Id
    private UUID id;

    @ManyToOne(optional = false)
    @JoinColumn(name = "line_id", nullable = false)
    private Line line; // Line 1 -> 0..* Cycle

    @ManyToOne(optional = false)
    @JoinColumn(name = "service_id", nullable = false)
    private Service service; // Service 1 -> 0..* Cycle

    private LocalDateTime dateDebut;
    private LocalDateTime dateFin;
    private boolean estActif;
}
