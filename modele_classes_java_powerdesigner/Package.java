package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "packages")
public class Package {
    @Id
    private UUID id;

    @Column(nullable = false, unique = true)
    private String code;

    @Column(nullable = false)
    private String nom;

    private String description;

    @Enumerated(EnumType.STRING)
    private TypeForfaitCode typeForfait;

    private BigDecimal prixMensuel;
    private String categoriePackage;
    private boolean estActif;
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "forfaitActif")
    private List<Line> lignes = new ArrayList<>(); // Package 1 -> 0..* Line
}
