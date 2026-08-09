package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "invoices")
public class Invoice {
    @Id
    private UUID id;

    @Column(nullable = false, unique = true)
    private String numeroFacture;

    private String type;
    private LocalDate periodeDebut;
    private LocalDate periodeFin;
    private String periodeLibelle;
    private BigDecimal montantTotal;
    private BigDecimal totalTtc;
    private boolean estPubliee;
    private LocalDateTime datePublication;

    @Enumerated(EnumType.STRING)
    private StatutFactureCode statut;

    private String fichierPdf;
    private LocalDateTime createdAt;

    @ManyToOne(optional = false)
    @JoinColumn(name = "contrat_id", nullable = false)
    private Contrat contrat; // Contrat 1 -> 0..* Invoice

    @ManyToOne
    @JoinColumn(name = "line_id")
    private Line line; // Line 0..1 -> 0..* Invoice

    @ManyToOne
    @JoinColumn(name = "type_facture_id")
    private TypeFacture typeFacture; // TypeFacture 0..1 -> 0..* Invoice

    @OneToMany(mappedBy = "invoice", cascade = CascadeType.ALL)
    private List<HistoriqueFacturation> historiques = new ArrayList<>(); // Invoice 1 -> 0..* HistoriqueFacturation
}
