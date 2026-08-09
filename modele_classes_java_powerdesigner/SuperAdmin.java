package com.moovafrica.powerdesigner;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;

@Entity
@Table(name = "super_admins")
public class SuperAdmin extends Utilisateur {
    // Héritage Utilisateur
}
