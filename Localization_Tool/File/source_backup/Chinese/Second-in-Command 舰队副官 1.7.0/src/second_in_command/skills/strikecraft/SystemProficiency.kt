package second_in_command.skills.strikecraft

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class SystemProficiency : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "所有具备舰船系统的战机"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("若舰船系统有充能：+1 充能数量", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("若舰船系统能回复充能：+40%% 回充速率", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("若舰船系统有冷却时间：-33%% 冷却时间", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())

    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {

    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun applyEffectsToFighterSpawnedByShip(data: SCData, fighter: ShipAPI?, ship: ShipAPI?, id: String?) {
        var stats = fighter!!.mutableStats

        stats.systemUsesBonus.modifyFlat(id, 1f)
        stats.systemRegenBonus.modifyPercent(id, 40f)
        stats.systemCooldownBonus.modifyMult(id, 0.666f)
    }

}