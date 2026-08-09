package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "lines")
public class Line {
    @Id
    private UUID id;

    @Column(nullable = false, unique = true)
    private String msisdn;

    private String nomUtilisateur;
    private String imsi;
    private String cycleCommercial;

    @Enumerated(EnumType.STRING)
    private CycleFacturationCode cycleFacturation;

    private boolean estActive;
    private LocalDateTime dateActivation;
    private LocalDateTime dateFin;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    private BigDecimal forfait;

    @ManyToOne(optional = false)
    @JoinColumn(name = "contrat_id", nullable = false)
    private Contrat contrat; // Contrat 1 -> 0..* Line

    @ManyToOne
    @JoinColumn(name = "employe_id")
    private Employe employe; // Employe 0..1 -> 0..* Line

    @ManyToOne
    @JoinColumn(name = "package_id")
    private Package forfaitActif; // Package 0..1 -> 0..* Line

    @OneToMany(mappedBy = "line", cascade = CascadeType.ALL)
    private List<LineService> lineServices = new ArrayList<>(); // Line 1 -> 0..* LineService

    @OneToMany(mappedBy = "line")
    private List<Cycle> cycles = new ArrayList<>(); // Line 1 -> 0..* Cycle

    @OneToMany(mappedBy = "line")
    private List<Invoice> factures = new ArrayList<>(); // Line 0..1 -> 0..* Invoice
}
