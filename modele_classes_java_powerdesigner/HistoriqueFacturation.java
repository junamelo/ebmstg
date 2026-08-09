package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "historique_facturation")
public class HistoriqueFacturation {
    @Id
    private UUID id;

    @ManyToOne(optional = false)
    @JoinColumn(name = "invoice_id", nullable = false)
    private Invoice invoice; // Invoice 1 -> 0..* HistoriqueFacturation

    @ManyToOne(optional = false)
    @JoinColumn(name = "agent_id", nullable = false)
    private AgentFacturation agent; // AgentFacturation 1 -> 0..* HistoriqueFacturation

    private String ancienStatut;
    private String nouveauStatut;
    private String commentaire;
    private LocalDateTime createdAt;
}
