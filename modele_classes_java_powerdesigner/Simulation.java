package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "simulations")
public class Simulation {
    @Id
    private UUID id;

    @ManyToOne(optional = false)
    @JoinColumn(name = "utilisateur_id", nullable = false)
    private Utilisateur utilisateur; // Utilisateur 1 -> 0..* Simulation

    @ManyToOne
    @JoinColumn(name = "line_id")
    private Line line; // Line 0..1 -> 0..* Simulation

    private Integer minutesPrevues;
    private Integer smsPrevus;
    private BigDecimal dataPrevueGo;
    private BigDecimal montantEstime;

    @Column(columnDefinition = "TEXT")
    private String parametresJson;

    private LocalDateTime createdAt;
}
