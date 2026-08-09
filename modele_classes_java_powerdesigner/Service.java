package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "services")
public class Service {
    @Id
    private UUID id;

    @Column(nullable = false, unique = true)
    private String code;

    @Column(nullable = false)
    private String nom;

    @Enumerated(EnumType.STRING)
    private TypeServiceCode typeService;

    private BigDecimal tarifUnitaire;
    private boolean estActif;
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "service")
    private List<LineService> lineServices = new ArrayList<>(); // Service 1 -> 0..* LineService

    @OneToMany(mappedBy = "service")
    private List<Cycle> cycles = new ArrayList<>(); // Service 1 -> 0..* Cycle
}
