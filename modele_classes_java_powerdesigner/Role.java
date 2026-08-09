package com.moovafrica.powerdesigner;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "roles")
public class Role {
    @Id
    private UUID id;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, unique = true)
    private RoleCode code;

    @Column(nullable = false)
    private String libelle;

    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "role")
    private List<Utilisateur> utilisateurs = new ArrayList<>(); // Role 1 -> 0..* Utilisateur
}
