package second_in_command.skills.piracy

import com.fs.starfarer.api.combat.MutableShipStatsAPI
import com.fs.starfarer.api.combat.ShipAPI
import com.fs.starfarer.api.combat.ShipVariantAPI
import com.fs.starfarer.api.impl.campaign.ids.Stats
import com.fs.starfarer.api.impl.campaign.skills.Salvaging
import com.fs.starfarer.api.ui.TooltipMakerAPI
import com.fs.starfarer.api.util.Misc
import second_in_command.SCData
import second_in_command.specs.SCBaseSkillPlugin

class GenerousDonation : SCBaseSkillPlugin() {

    override fun getAffectsString(): String {
        return "舰队和打捞行动"
    }

    override fun addTooltip(data: SCData, tooltip: TooltipMakerAPI) {

        tooltip.addPara("+60%% 战后物品打捞量", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        tooltip.addPara("+25%% 敌舰击沉后武器掉落概率", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())
        //tooltip.addPara("+1 当舰队处于 缓速航行* 时的最大宇宙航行速度", 0f, Misc.getHighlightColor(), Misc.getHighlightColor())


    }

    override fun applyEffectsBeforeShipCreation(data: SCData, stats: MutableShipStatsAPI?, variant: ShipVariantAPI, hullSize: ShipAPI.HullSize?, id: String?) {


    }

    override fun applyEffectsAfterShipCreation(data: SCData, ship: ShipAPI?, variant: ShipVariantAPI, id: String?) {

    }

    override fun advance(data: SCData, amount: Float) {
        data.fleet.stats.dynamic.getStat(Stats.BATTLE_SALVAGE_MULT_FLEET).modifyFlat("sc_generous_donation", 0.6f)
        data.fleet.stats.dynamic.getMod(Stats.ENEMY_WEAPON_RECOVERY_MOD).modifyFlat("sc_generous_donation", 0.25f)
        data.fleet.stats.dynamic.getMod(Stats.ENEMY_WING_RECOVERY_MOD).modifyFlat("sc_generous_donation", 0.25f)
        //data.fleet.stats.dynamic.getMod(Stats.MOVE_SLOW_SPEED_BONUS_MOD).modifyFlat("sc_generous_donation", 1f, "慷慨捐赠")
    }

    override fun onActivation(data: SCData) {
        data.fleet.stats.dynamic.getStat(Stats.BATTLE_SALVAGE_MULT_FLEET).modifyFlat("sc_generous_donation", 0.6f)
        data.fleet.stats.dynamic.getMod(Stats.ENEMY_WEAPON_RECOVERY_MOD).modifyFlat("sc_generous_donation", 0.25f)
        data.fleet.stats.dynamic.getMod(Stats.ENEMY_WING_RECOVERY_MOD).modifyFlat("sc_generous_donation", 0.25f)
        //data.fleet.stats.dynamic.getMod(Stats.MOVE_SLOW_SPEED_BONUS_MOD).modifyFlat("sc_generous_donation", 1f, "慷慨捐赠")
    }

    override fun onDeactivation(data: SCData) {
        data.fleet.stats.dynamic.getStat(Stats.BATTLE_SALVAGE_MULT_FLEET).unmodify("sc_generous_donation")
        data.fleet.stats.dynamic.getMod(Stats.ENEMY_WEAPON_RECOVERY_MOD).unmodify("sc_generous_donation")
        data.fleet.stats.dynamic.getMod(Stats.ENEMY_WING_RECOVERY_MOD).unmodify("sc_generous_donation")
        //data.fleet.stats.dynamic.getMod(Stats.MOVE_SLOW_SPEED_BONUS_MOD).unmodify("sc_generous_donation")
    }
}